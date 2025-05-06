"""
arXiv 论文下载器

用于下载 arXiv 论文的 PDF 文件
"""

import os
import logging
import requests
from pathlib import Path
from typing import Optional, Union, Tuple
from .arxiv_client import ArxivClient, ArxivPaper

logger = logging.getLogger(__name__)

def download_paper(
    paper_id: str,
    output_dir: Union[str, Path],
    filename: Optional[str] = None,
    get_metadata: bool = True,
) -> Tuple[str, Optional[ArxivPaper]]:
    """
    下载 arXiv 论文的 PDF
    
    Args:
        paper_id: arXiv 论文 ID，如 "1706.03762" 或完整的链接
        output_dir: 保存 PDF 的目录
        filename: 文件名（不含扩展名），如果为 None，则使用论文 ID 作为文件名
        get_metadata: 是否获取论文的元数据
    
    Returns:
        tuple: (保存的 PDF 路径, 论文元数据对象或 None)
    """
    # 从链接中提取ID
    if '/' in paper_id and ('arxiv.org' in paper_id or 'abs' in paper_id):
        paper_id = paper_id.split('/')[-1]
    
    # 去除版本号
    if 'v' in paper_id and paper_id[paper_id.find('v')-1].isdigit():
        paper_id = paper_id.split('v')[0]
    
    output_dir = Path(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取元数据（如果需要）
    metadata = None
    if get_metadata:
        try:
            client = ArxivClient()
            metadata = client.get_by_id(paper_id)
            if not filename:
                filename = metadata.filename
        except Exception as e:
            logger.warning(f"获取论文 {paper_id} 的元数据失败: {e}")
    
    # 如果没有指定文件名，使用ID
    if not filename:
        filename = paper_id.replace('/', '_')
    
    # 确保文件名以 .pdf 结尾
    if not filename.endswith('.pdf'):
        filename = f"{filename}.pdf"
    
    # 构建 PDF URL
    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    
    # 构建目标路径
    output_path = output_dir / filename
    
    # 下载 PDF
    logger.info(f"正在从 {pdf_url} 下载论文到 {output_path}")
    
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        # 检查是否是PDF（通过Content-Type或文件头）
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower() and response.content[:4] != b'%PDF':
            raise ValueError(f"下载的文件不是PDF: {content_type}")
        
        # 写入文件
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"论文已保存到 {output_path}")
        return str(output_path), metadata
    
    except Exception as e:
        logger.error(f"下载论文 {paper_id} 失败: {e}")
        raise