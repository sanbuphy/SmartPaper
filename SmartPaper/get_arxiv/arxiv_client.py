"""
arXiv API 客户端，用于搜索和获取 arXiv 论文的元数据
"""

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import urllib.parse
import requests
import feedparser
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class ArxivPaper:
    """arXiv 论文的元数据"""
    
    # 论文ID（不包含版本号）
    paper_id: str
    
    # 论文标题
    title: str
    
    # 论文摘要
    abstract: str
    
    # 作者列表
    authors: List[str]
    
    # 分类
    categories: List[str]
    
    # 主分类
    primary_category: str
    
    # 发布日期
    published: datetime
    
    # 更新日期
    updated: datetime
    
    # PDF URL
    pdf_url: str
    
    # arXiv页面URL
    web_url: str
    
    # DOI
    doi: Optional[str] = None
    
    # 评论
    comment: Optional[str] = None
    
    # 期刊引用
    journal_ref: Optional[str] = None
    
    @property
    def filename(self) -> str:
        """返回适合作为文件名的字符串"""
        safe_title = self.title.replace('/', '_').replace('\\', '_')[:50]
        return f"{self.paper_id.replace('/', '_')}_{safe_title}"
    
    def __str__(self) -> str:
        return f"{self.title} ({self.paper_id})"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return dataclasses.asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArxivPaper':
        """从字典创建实例"""
        # 处理日期字段
        for date_field in ['published', 'updated']:
            if isinstance(data.get(date_field), str):
                data[date_field] = datetime.fromisoformat(data[date_field])
        
        return cls(**data)


class ArxivClient:
    """
    arXiv API 客户端
    
    用于搜索和获取 arXiv 论文的元数据
    """
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    # arXiv API 限制：每秒最多调用 1 次
    REQUEST_INTERVAL = 3  # 秒
    
    def __init__(self):
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """遵守 arXiv API 速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.REQUEST_INTERVAL:
            sleep_time = self.REQUEST_INTERVAL - elapsed
            logger.debug(f"等待 {sleep_time:.2f} 秒以遵守 API 速率限制")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _parse_entry(self, entry: Dict[str, Any]) -> ArxivPaper:
        """
        解析 arXiv API 返回的条目
        """
        # 提取 arXiv ID (不包含版本号)
        arxiv_id = entry.id.split('arxiv.org/abs/')[-1]
        if '/' in arxiv_id and 'v' not in arxiv_id:
            # 旧格式 ID，保持原样
            paper_id = arxiv_id
        else:
            # 新格式 ID，删除版本号
            paper_id = arxiv_id.split('v')[0]
        
        # 提取作者
        if hasattr(entry, 'authors'):
            authors = [author.name for author in entry.authors]
        else:
            authors = [entry.get('author', '未知作者')]
        
        # 分类
        categories = []
        if 'tags' in entry:
            categories = [tag.term for tag in entry.tags]
        elif 'arxiv_primary_category' in entry:
            categories = [entry.arxiv_primary_category.get('term', '')]
        
        primary_category = ''
        if hasattr(entry, 'arxiv_primary_category'):
            primary_category = entry.arxiv_primary_category.get('term', '')
        elif categories:
            primary_category = categories[0]
        
        # 解析日期
        published = datetime(*entry.published_parsed[:6])
        updated = datetime(*entry.updated_parsed[:6])
        
        # 构建 URL
        pdf_url = f"http://arxiv.org/pdf/{arxiv_id}"
        web_url = f"http://arxiv.org/abs/{arxiv_id}"
        
        # 可选元数据
        comment = entry.get('arxiv_comment', None)
        journal_ref = entry.get('arxiv_journal_ref', None)
        doi = entry.get('arxiv_doi', None)
        
        return ArxivPaper(
            paper_id=paper_id,
            title=entry.title,
            abstract=entry.summary,
            authors=authors,
            categories=categories,
            primary_category=primary_category,
            published=published,
            updated=updated,
            pdf_url=pdf_url,
            web_url=web_url,
            doi=doi,
            comment=comment,
            journal_ref=journal_ref
        )
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending",
        start: int = 0,
    ) -> List[ArxivPaper]:
        """
        搜索 arXiv 论文
        
        Args:
            query: 搜索查询字符串
            max_results: 最大结果数，默认为 10
            sort_by: 排序方式，可选 "relevance", "lastUpdatedDate", "submittedDate"
            sort_order: 排序顺序，可选 "ascending", "descending"
            start: 结果的起始索引
            
        Returns:
            论文列表
        """
        self._respect_rate_limit()
        
        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}?{query_string}"
        
        logger.info(f"正在搜索 arXiv: {query}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"arXiv API 返回错误状态码: {response.status_code}")
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        papers = []
        for entry in feed.entries:
            try:
                paper = self._parse_entry(entry)
                papers.append(paper)
            except Exception as e:
                logger.error(f"解析条目时出错: {e}")
                continue
        
        logger.info(f"找到 {len(papers)} 篇论文")
        return papers
    
    def get_by_id(self, paper_id: str) -> ArxivPaper:
        """
        通过 ID 获取论文
        
        Args:
            paper_id: arXiv 论文 ID，如 "1706.03762"
        
        Returns:
            论文对象
        """
        self._respect_rate_limit()
        
        # 确保ID格式正确
        clean_id = paper_id.replace("arxiv:", "").strip()
        
        params = {
            "id_list": clean_id
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}?{query_string}"
        
        logger.info(f"正在获取 arXiv 论文: {clean_id}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"arXiv API 返回错误状态码: {response.status_code}")
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        if not feed.entries:
            raise ValueError(f"找不到 ID 为 {clean_id} 的论文")
        
        return self._parse_entry(feed.entries[0])
    
    def get_by_ids(self, paper_ids: List[str]) -> List[ArxivPaper]:
        """
        通过多个 ID 批量获取论文
        
        Args:
            paper_ids: arXiv 论文 ID 列表
        
        Returns:
            论文对象列表
        """
        self._respect_rate_limit()
        
        # 确保ID格式正确
        clean_ids = [id.replace("arxiv:", "").strip() for id in paper_ids]
        
        params = {
            "id_list": ','.join(clean_ids)
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}?{query_string}"
        
        logger.info(f"正在批量获取 arXiv 论文: {clean_ids}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"arXiv API 返回错误状态码: {response.status_code}")
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        papers = []
        for entry in feed.entries:
            try:
                paper = self._parse_entry(entry)
                papers.append(paper)
            except Exception as e:
                logger.error(f"解析条目时出错: {e}")
                continue
        
        return papers