## 第1页

---

![《高级工程研究》期刊封面](images\page1_img1.jpeg)
> 《高级工程研究》期刊封面：这是一张期刊封面图，展示了《International Journal of Advanced Engineering Research and Science》的封面设计。包含期刊名称、卷号（Vol-7）、期号（Issue-10）、出版月份（Oct 2020）、DOI信息以及AI Publications的标志。封面设计以蓝色多面体图案为背景，整体风格现代简洁，用于标识和宣传该期学术期刊。

![IAERS期刊标志图](images\page1_img2.jpeg)
> IAERS期刊标志图：这是一张[标志图]，展示了[International Journal of Advanced Engineering Research and Science (IAERS)的标志]。包含[IAERS的英文缩写和全称]。[标志设计简洁，以蓝色和白色为主，背景为黑色]。图像的可能用途是[作为期刊的标识，用于期刊封面、网站或其他宣传材料中]。

 
International Journal of Advanced Engineering Research and 
Science (IJAERS) 
Peer-Reviewed Journal 
ISSN: 2349-6495(P) | 2456-1908(O) 
Vol-10, Issue-12; Dec, 2023 
Journal Home Page Available: https://ijaers.com/ 
Article DOI:https://dx.doi.org/10.22161/ijaers.1012.1  
 
 
www.ijaers.com                                                                                Page | 1  
Study on Control of Inverted Pendulum System Based on 
Simulink Simulation 
Yongsheng Li, Jiahui Feng, Ruei-Yuan Wang, Ho-Sheng Chen, Yongzhen Gong* 
 
School of Mechanical and Electrical Engineering, Guangdong University of Petrochem Technology (GDUPT), Maoming 525000, China 
*Corresponding author 
 
Received: 06 Oct 2023, 
Receive in revised form: 10 Nov 2023, 
Accepted: 22 Nov 2023, 
Available online: 05 Dec 2023 
©2023 The Author(s). Published by AI 
Publication. This is an open access article 
under 
the 
CC 
BY 
license 
(https://creativecommons.org/licenses/by/4.0/). 
Keywords— 
Inverted 
pendulum 
system, 
Proportional 
integral 
differential 
(PID) 
control, Fuzzy PID control, Nonlinear 
dynamic system, Simulink simulation 
 
Abstract— This study aims to conduct control research on an inverted 
pendulum system using the Simulink simulation platform. The inverted 
pendulum system is a classic nonlinear dynamic system with important 
theoretical and practical applications. Firstly, establish a mathematical 
model of the inverted pendulum system, including the dynamic equation of 
the pendulum rod and the sensor measurement model. Subsequently, the 
PID (proportional integral differential) controller design method based on 
the inverted pendulum system and the fuzzy PID controller design methods 
were verified through simulation experiments. The ultimate goal is for the 
designed fuzzy PID controller to effectively stabilize the inverted pendulum 
system in the vertical position and achieve fast tracking of the target 
position. Simulation and experimental results show that compared to 
traditional PID controllers, fuzzy PID controllers can quickly stabilize the 
pendulum in the target position and have good practicality, stability, speed, 
and accuracy. Future research can further explore the application of other 
advanced control strategies in inverted pendulum systems, as well as their 
potential applications in practical engineering. 
 
I. 
INTRODUCTION 
The initial research on inverted pendulums began in 
the 1950s, designed by control theory experts at the 
Massachusetts Institute of Technology (MIT) in the United 
States based on the principle of rocket launch boosters. 
The inverted pendulum system, as the model foundation 
for shipborne radar, rocket launch systems, and satellite 
attitude control, has been the focus of many researchers in 
the past few decades. The research on inverted pendulums 
will tend towards more complex and in-depth studies. 
Inverted pendulum systems can be divided into linear 
inverted pendulums, planar inverted pendulums, composite 
inverted pendulums, etc. according to their composition. 
According to their complexity, they can be divided into 
primary inverted pendulum systems, secondary inverted 
pendulum systems, tertiary inverted pendulum systems, 
and multi-level inverted pendulum systems. The first-level 
inverted pendulum system consists of a driving motor, a 
conveyor belt, a pendulum rod, a small car, and a test 
bench [1, 2, 3 ]. The first-level linear inverted pendulum 
system is driven by an electric motor and is an unstable, 
nonlinear, single-input, double-output, strongly coupled 




---

## 第2页

---

![倒立摆系统控制流程](images\page2_img1.png)
> 倒立摆系统控制流程：这是一张示意图，展示了倒立摆控制系统的工作流程。包含计算机、伺服执行器、直流电机、倒立摆、数据采集卡、编码器1和编码器2等关键信息点。文本标签清晰标注了每个组件及其连接关系。图像的可能用途是解释倒立摆控制系统的组成和数据流动过程。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 2  
system [4, 5, 6, 14, 15]. It controls both the angle of the 
pendulum and the position of the trolley to be stable, and 
the steady-state errors of the trolley position and pendulum 
angle must be controlled within a small range. 
The control of the inverted pendulum is a difficult 
point in the study of inverted pendulum control, and there 
have been many studies on the inverted pendulum, which 
are basically based on the assumption that the trolley track 
of the inverted pendulum system is sufficiently long [7]. 
With the development of technology, new control methods 
are constantly emerging, and people use inverted 
pendulums to test whether new control methods can 
handle multivariable, nonlinear, and absolute instability. 
The inverted pendulum has become an ideal experimental 
method for testing the effectiveness of control strategies 
[8]. This article focuses on a first-order inverted pendulum 
system. Firstly, a mathematical model is established using 
the knowledge of Newtonian mechanics, and then a 
simulation model of the inverted pendulum system is 
established using the Simulink module of MTALAB [9, 10, 
11, 13]. Finally, by comparing and analyzing the curves 
and parameters of the established traditional PID controller 
and fuzzy PID controller, this study is trying to find out 
whether the fuzzy PID control method is better or not than 
the ordinary PID control method in terms of stability and 
speed. 
 
II. 
ESTABLISHING MATHEMATICAL MODEL 
The working principle of a first-order linear inverted 
pendulum (Figure 1) is that when the data acquisition card 
transmits the collected data from the rotary encoder to the 
computer and compares it with the set value. The deviation 
is processed through some calculation, and a control law is 
issued to control the motor to make the pendulum swing 
left and right into the stable range, thereby achieving the 
pendulum to stand upright and not fall, as well as 
self-swing [12]. 
 
Fig.1 Working Principle Diagram of a First Level Linear Inverted Pendulum 
 
Because establishing a mathematical model of the 
system is the foundation for studying control methods, the 
first step is to model the inverted pendulum system in this 
paper. And mathematical modeling is carried out using the 
Newtonian mechanics method to obtain the state-space 
equation of the system and prepare for the subsequent 
controller design and simulation. 
The model parameters of the inverted pendulum 
system are the pendulum mass m1=0.109kg, the trolley 
mass m2=1.096kg g, the angle between the pendulum and 
the vertical direction θ (rad), the distance from the center 
of the swing rod to the car l=0.25m, the distance the car 
moves x (m), the force applied to the car f (N), the friction 
coefficient of the car rf =0.1N/m/sec, the inertia of the 
swing 
rod 
I=0.0034kg*m2, 
and 
the 
gravitational 
acceleration g=9.8N/ m2. The physical model diagram of 
the inverted pendulum system is shown in Figure 2. A 
detailed decomposition of various forces acting on the 
pendulum and trolley using Newtonian mechanics 
methods is shown in Figure 3. P and N are set as the 
components of the interaction force in the vertical and 
horizontal directions during the movement or stability of 
the car. 




---

## 第3页

---

![车辆摆杆动力学模型](images\page3_img1.jpeg)
> 车辆摆杆动力学模型：这是一张示意图，展示了带有摆杆的车辆系统模型。包含车辆质量（m2）、摆杆长度（2l）、摆杆角度（φ）、作用力（F）、以及车辆位置（xc）和速度（r1x）等关键信息。图中标注了“swing rod”和“car”，并显示了力和运动方向。图像可能用于解释车辆动力学或摆杆系统在车辆运动中的作用。

![斜面受力分析示意图](images\page3_img2.jpeg)
> 斜面受力分析示意图：这是一张示意图，展示了物体在斜面上的受力分析。包含重力（m₁g）、垂直于斜面的支持力（N）、平行于斜面的推力（P）以及角度θ和φ。图中标注了力的方向和角度关系。图像可能用于物理教学，解释斜面上物体的受力平衡和力的分解。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 3  
 
Fig.2 Physical Model of Inverted Pendulum System 
 
 
Fig.3 Force Analysis Diagram of the Small Car and 
Swing Rod 
 
According to Figure 3, first analyze the force in the 
horizontal direction. 
   𝑚2𝑥̈ = 𝐹−𝑟𝑓𝑥̇ −𝑁                                                     (1) 
N = 𝑚1
𝑑2
𝑑𝑡2 (𝑥+ 𝑙sin 𝜃) = 𝑚1𝑥̈ + 𝑚1𝑙𝜃̈ cos 𝜃−
𝑚1𝑙𝜃2̇ sin 𝜃                    (2) 
Substituting equation (2) into equation (1) yields the 
equation of motion in the horizontal direction 
 (𝑚1 + 𝑚2)𝑥̈ + 𝑟𝑓𝑥̇ + 𝑚1𝑙𝜃̈ cos 𝜃−𝑚1𝑙𝜃2̇ sin 𝜃=
𝐹                         (3) 
In the vertical direction, as the car is used as the horizontal 
plane, only the force acting on the swing rod needs to be 
analyzed to obtain 
P −𝑚1g = 𝑚1
𝑑2
𝑑𝑡2 (𝑙cos 𝜃) = −𝑚1𝑙𝜃̈ sin 𝜃−
𝑚1𝑙𝜃̈ sin 𝜃−𝑚1𝑙𝜃̇ 2 cos 𝜃       (4) 
The torque balance equation is 
−P𝑙sin 𝜃−𝑁𝑙cos 𝜃= I𝜃̈                                                    (5) 
The second equation of motion can be obtained by using 
equations (2) and (4) 
(I + 𝑚1𝑙2)𝜑̈ −𝑚1g𝑙𝜑̇ = 𝑚1𝑙𝑥̈                                           (6) 
Set angle θ= π+ φ， and φ after being converted to radians, 
it is much less than 1 rad, that is φ ≪1. So it can be 
simplified as cos 𝜃= −1, and sin 𝜃= −𝜑，(
𝑑𝜃
𝑑𝑡)
2
= 0. 
Using u instead of the input force F, equations (3) and (6) 
can be simplified as: 
{  (I + 𝑚1𝑙2)𝜑̈ −𝑚1g𝑙𝜑=̇
𝑚1𝑙𝑥̈
   (𝑚2 + 𝑚)𝑥̈ + 𝑟𝑓 𝑥̇ −𝑚1 𝑙𝜑̈ = 𝑢                                              
(7) 
Perform a Laplace transform on the above equation, which 
will be 
   { (I + 𝑚1𝑙2)Φ(𝑠)𝑠2 −𝑚1g𝑙Φ(𝑠) = 𝑚1𝑙Χ(𝑠)𝑠2        
  (𝑚2 + 𝑚)Χ(𝑠)𝑠2 + 𝑟𝑓Χ(𝑠)𝑠 −𝑚1 𝑙Φ(𝑠)𝑠2 = 𝑈(𝑆)                      
(8)  
The first equation in the above equation can be written as 
follows: 
     
Φ(𝑆)
𝑋(𝑆) =
𝑚1𝑙𝑠2
(𝐼+𝑚1𝑙2)−𝑚1g𝑙                                                  (9) 
Substitute equation (9) into the equation with the control 
input in equation (8), which will be 
 
𝜙(𝑆)
𝑈(𝑆)   =
 
𝑚1𝑙
𝑤𝑠2
𝑠4+
𝑟𝑓(𝐼+𝑚1𝑙2)
𝑤
𝑠3−(𝑚1+𝑚2)𝑚1g𝑙
𝑤
𝑠2−
𝑟𝑓𝑚1g𝑙
𝑤
𝑠
                                          
(10) 
wherein，w = [(𝑚1 + 𝑚2)(𝐼+ 𝑚1𝑙2) −(𝑚1𝑙)2]。 
Using equation (7) for 𝑥̈ and𝜑̈ solve, which will be 
{
   
 
   
 
𝑥̇ = 𝑥̈
 
𝑥̈ = 
−(𝐼+𝑚1𝑙2)𝑟𝑓
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝑥̇ +
𝑚12g𝑙2
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝜑+
(𝐼+𝑚1𝑙2)
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝑢
 
𝜑̇ = 𝜑̈
 
𝜑̈ = 
𝑚1𝑙𝑟𝑓
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝑥̇ +
𝑚1g𝑙(𝑚1+𝑚2)
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝜑+
𝑚1𝑙
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 𝑢
 
            
(11) 
Compiled into a standard state space equation as 
 
[
𝑥̇
𝑥̈
𝜑̇
𝜑̈
]=
[
 
 
 
 0
1
0
0
0
−(𝐼+𝑚1𝑙2)𝑟𝑓
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
𝑚12g𝑙2
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
0
0
0
0
1
0
𝑚1𝑙𝑟𝑓
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
𝑚1g𝑙(𝑚1+𝑚2)
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
0]
 
 
 
 
[
𝑥
𝑥̇
𝜑
𝜑̇
]+ 
[
 
 
 
 
0
(𝐼+𝑚1𝑙2)
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
0
𝑚1𝑙
(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2]
 
 
 
 
𝑢  (12) 




---

## 第4页

---

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 4  
   y = [𝑥
𝜃] = [1
0
0
0
0
0
1
0] [
𝑥
𝑥̇
𝜑
𝜑̇
] 
If the pendulum is regarded as a rod with uniform mass, 
then the inertia of the pendulum is 
  I =
1
3 𝑚1𝑙2                                                                            (13) 
Substituting equation (13) into the first equation of 
equation (7) yields 
 (
1
3 𝑚1𝑙2 + 𝑚1𝑙2) 𝜑̈ −𝑚1g𝑙𝜑̇ = 𝑚1𝑙𝑥̈              (14) 
Simplify the above equation, which will be 
𝜑̈ =
3g
4𝑙𝜑+
3
4𝑙𝑥̈                                                 (15) 
Let the system state space equation be 
{𝑋̇ = 𝐴𝑋+ 𝐵𝑢′ 
𝑌= 𝐶𝑋+ 𝐷𝑈                               (16) 
Let X = [𝑥̇
𝑥̈
𝜃̇
𝜃̈], u'  = ẍ，The following state 
space expression can be obtained 
   [
𝑥̇
𝑥̈
𝜑̇
𝜑̈
] =
[
 
 
 0
1
0
0
0
0
0
0
0
0
0
1
0
0
0
3g
4𝑙]
 
 
 
[
𝑥
𝑥̇
𝜑
𝜑̇
] +
[
 
 
 0
1
0
3
4𝑙]
 
 
 
𝑢′              (17) 
  Y = [𝑥
𝜃] = [1
0
0
0
0
0
1
0] [
𝑥
𝑥̇
𝜑
𝜑̇
] 
 
III. 
CONTROLLER DESIGN AND FUZZY LOGIC 
ESTABLISHMENT  
Firstly, traditional PID is used to design PID 
controllers for the output displacement and output angle of 
the system. Through parameter tuning and control, the 
spatial-state equation output reaches a stable state. When 
studying the displacement of a small car, the spatial state 
control equation of the system is obtained by inputting the 
car parameters into equation (17) as follows: 
{
 
 
 
 
                𝑋= [
0
1
0
0
0
0
0
0
0
0
0
1
0
0
0
29.4
] 𝑋+ [
0
1
0
0.75
] 𝑢
′
 
 
Y = [𝑥] = [1
0
0
0]𝑋
           (18) 
We first use the traditional PID control method to 
control the spatial-state equation of displacement output 
and simulate it using Simulink in Matlab. We then adjust a 
suitable set of PID parameters through parameter tuning 
principles. The input is the unit step signal, and the PID 
parameter is Kp= 70, KI = 0.7, KD = 6 the system reaches 
steady state at time T=0.08S. 
The fuzzy controller designed here is a two-input, 
three-output fuzzy PID controller, and the two output 
signals jointly use a fuzzy rule. The input is the error e= 
r(k)-y(k) and error change rate ec = e(k)-e(k-1) between 
the given value and the actual value of the car 
displacement or swing rod angle, and the output is the 
corrected values ΔKp, ΔKI, andΔKD of the PID parameters. 
In this design, the basic domain of error e is taken as 
[-5, 5], and the basic domain of error change rate ec is 
taken as [-5, 5]. The domain of the output variablesΔKp, 
ΔKI, andΔKD  are taken as [-3, 3]. 
In order to obtain the input of the fuzzy controller, it 
is necessary to fuzzify the precise quantity, that is, 
multiply the input quantity by the corresponding 
quantization factor, and convert it from the basic domain 
to the corresponding fuzzy domain. The quantization 
factor of error e isαe=0.8, and the factor of error change 
rate ec is αec=0.2. The control quantity obtained through 
the fuzzy control algorithm is a fuzzy quantity that needs 
to be multiplied by a proportional factor and converted 
into the basic domain. When the output variable is the 
displacement of the car, the scaling factor ofΔKp,ΔKI,ΔKD 
areαΔKp =αΔKI =1,αΔKD =-5. When taking the output variable 
swing 
angle, 
the 
scaling 
factor 
of 
ΔKp,ΔKI,ΔKD 
areαΔKp=200,αΔKI=1,αΔKD=30 
Divide the fuzzy domain of input variables(e, ec) and 
output variables (ΔKp,ΔKI,ΔKD) into 7 fuzzy subsets, 
namely NB, NM, NS, ZO, PS, PM, PB representing 
negative big, negative medium, negative small, zero, 
positive small, positive medium, and positive big, 
respectively. The membership functions of input variables 
and output variables both adopt triangular membership 
functions, as shown in Figure 4. 




---

## 第5页

---

![模糊逻辑隶属函数分布图](images\page5_img1.png)
> 模糊逻辑隶属函数分布图：这是一张图表，展示了模糊逻辑系统中的隶属函数分布。包含NB、NM、NS、O、PS、PM、PB等标签，表示不同的隶属度区间。图像中有一条红色的线和一个黑色的点，可能用于指示特定的输入值及其对应的隶属度。图像的可能用途是解释模糊逻辑控制器中输入变量的模糊化过程。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 5  
 
Fig.4 The Membership Function of e, ec,ΔKp,ΔKI,ΔKD 
 
The fuzzy rule statement used by the output variable fuzzy controller is as follows: 
“if E isαand EC isβthen U isγ” Wherein,α,β,γboth represent the fuzzy sets corresponding to each variable. 
Based on the impact of PID parameters on system performance, parameter tuning principles, expert experience, and 
cognition, 49 control rules were obtained after processing, as shown in Tables 1–3. 
Table 1 Fuzzy Rule Table ofΔKp 
 
NB 
NM 
NS 
O 
PS 
PM 
PB 
NB 
PB 
PB 
PB 
PB 
PM 
PS 
O 
NM 
PB 
PB 
PB 
PB 
PM 
O 
O 
NS 
PM 
PM 
PM 
PM 
O 
PS 
PS 
O 
PM 
PM 
PS 
O 
NS 
NS 
NM 
PS 
PS 
PS 
O 
NS 
NM 
NM 
NM 
PM 
PS 
O 
NS 
NM 
NM 
NM 
NB 
PB 
O 
O 
NM 
NM 
NM 
NB 
NB 
 
Table 2 Fuzzy Rule Table ofΔKI 
 
NB 
NM 
NS 
O 
PS 
PM 
PB 
NB 
NB 
NB 
NM 
NM 
NS 
O 
O 
NM 
NB 
NB 
NM 
NS 
NS 
O 
O 
NS 
NB 
NM 
NS 
NS 
O 
PS 
PS 
O 
NM 
NM 
NS 
O 
PS 
PM 
PM 
PS 
NM 
NS 
O 
PS 
PS 
PM 
PB 
PM 
O 
O 
PS 
NM 
PM 
PB 
PB 
PB 
O 
O 
PS 
PM 
PM 
PB 
PB 
𝐾𝐼 
 
E 
EC 
𝐾𝑃 
 
EC 
E 




---

## 第6页

---

![模糊PID控制器设计界面](images\page6_img1.png)
> 模糊PID控制器设计界面：这是一张示意图，展示了模糊PID控制器的设计界面。包含两个输入变量E和EC，以及三个输出变量P、I和D。界面中显示了FIS名称为Fuzzy_PID，类型为Mamdani，以及相关的逻辑运算方法和规则设置。图像可能用于说明模糊逻辑控制器的配置和参数调整。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 6  
Table 3 Fuzzy Rule Table ofΔKD 
 
NB 
NM 
NS 
O 
PS 
PM 
PB 
NB 
PS 
NS 
NB 
NB 
NB 
NM 
PS 
NM 
PS 
NS 
NB 
NM 
NM 
NS 
O 
NS 
O 
NS 
NM 
NM 
NM 
NS 
O 
O 
O 
NS 
NS 
NS 
NS 
NS 
O 
PS 
O 
O 
O 
O 
O 
O 
O 
PM 
PB 
PS 
PS 
PS 
PS 
PS 
PB 
PB 
PB 
PM 
PM 
PM 
PS 
PS 
PB 
 
This design system uses the Mamdani inference 
method to perform fuzzy inference on the established 
fuzzy rules in order to obtain control variables. Meanwhile, 
using the center of gravity method to solve the fuzziness of 
language expression, thus obtaining the exact value 
ofΔKp,ΔKI,ΔKD. In addition, the values obtained through 
fuzzy reasoning and deblurring are multiplied by the 
corresponding scaling factors to obtain the incremental 
adjustment values of PID parameters, which are then 
substituted into equations (19) - (21) to obtain the control 
parameters of the PID controller. 
𝐾𝑃= 𝐾𝑃0 + △𝐾𝑃                                                       (19) 
𝐾𝐼= 𝐾𝐼0 +  △𝐾𝐼                                                        (20) 
𝐾𝐷= 𝐾𝐷0 +  △𝐾𝐷                                                     (21) 
 
Before establishing a fuzzy logic controller, the Tool 
Box parameters of the fuzzy logic system need to be set in 
Simulink (Figure 5). Then use the membership function 
parameter setting process of Tool Box (Figure 6) to 
establish the membership function of e, ec,ΔKp,ΔKI,ΔKD. 
 
Fig.5 Fuzzy Logic System Tool Box 
 
𝐾𝐷 
 
E 
EC 




---

## 第7页

---

![模糊PID控制器隶属函数图](images\page7_img1.png)
> 模糊PID控制器隶属函数图：这是一张图表，展示了模糊PID控制器的隶属函数编辑器界面。包含FIS变量、隶属函数图和参数设置等关键信息。文本标签包括“E”、“P”、“EC”、“D”等变量名称，以及“NB”、“NM”、“NS”等隶属函数名称。图像可能用于模糊逻辑系统的设计和调试，特别是PID控制器的参数调整。

![控制系统信号流图](images\page7_img2.jpeg)
> 控制系统信号流图：这是一张示意图，展示了两个控制系统的结构和信号流。包含关键信息点如增益模块（Gain11、Gain12、Gain13）、积分器（Integrator1）、微分器（Derivative2）、状态空间模型（State-Space4和State-Space5）、模糊PID控制器（Fuzzy pid2）以及信号加法器（Sum3、Sum4）和输出显示（Scope5、Scope6、Scope7）。文本标签包括各模块名称和参数值，如“70”、“0.7”、“6”等。图像可能用于解释和分析控制系统的设计和性能。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 7  
 
Fig.6 Membership Function of Fuzzy Logic System  
 
After setting the above parameters, they can be 
added to the rule editor, and all output surfaces of the 
fuzzy inference system can be observed in the output 
surface observer. 
 
IV. 
COMPARISON BETWEEN TRADITIONAL 
PID CONTROL AND FUZZY PID CONTROL 
Through Simulink simulation (Figure 7 and Figure 
8), it was found that, under appropriate parameters, 
traditional PID controllers have good control effects on the 
control object that can assume an accurate mathematical 
model. They can meet the requirements of system control 
accuracy and rise time, but there are problems such as long 
adjustment times. The fuzzy PID controller can adjust the 
PID parameters of the system in real time. By doing so, the 
PID parameters can be more suitable for the control 
requirements of the system, resulting in better control 
effects than traditional PID controllers (Figure 9). 
 
Fig.7 Simulink Simulations of Traditional PID and Fuzzy PID Control Systems (Swing Angle)  
 




---

## 第8页

---

![信号处理控制系统图示](images\page8_img1.jpeg)
> 信号处理控制系统图示：这是一张示意图，展示了控制系统中的信号处理流程。包含信号输入、增益调整、模糊逻辑控制器、积分器和多个加法器等关键信息点。文本标签包括“E”、“Gain1”、“Fuzzy Logic Controller1”、“Integrator”等。图像可能用于解释控制系统的设计和信号处理的逻辑关系。

![PID与模糊PID控制对比图](images\page8_img2.jpeg)
> PID与模糊PID控制对比图：这是一张[图表]，展示了[传统PID控制和模糊PID控制的仿真比较]。包含[时间（秒）与控制效果的对比曲线]。[图中显示了PID控制器和模糊PID控制器的响应曲线，模糊PID控制器的响应更快且更稳定]。图像的可能用途是[用于分析和比较不同控制策略的性能]。

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 8  
 
Fig.8 Simulink Simulation of a Fuzzy PID Controller for Swing Angle 
 
 
Fig.9 Response Curves of Traditional PID and Fuzzy PID Controller Systems (Swing Angle) 
 
V. 
CONCLUSIONS 
The inherent first-order linear inverted pendulum 
system is a typical single-input, multiple-output nonlinear 
system. This article analyzes the motion of the inherent 
first-order linear inverted pendulum system, establishes a 
mathematical model of the first-order linear inverted 
pendulum system using the Newtonian mechanics method, 
and designs PID controllers and fuzzy PID controllers to 
control the first-order linear inverted pendulum system 
separately.  
By adjusting their proportional constant and integral 
constant, the three parameters of the differential constant 
enable the first-order linear inverted pendulum system to 
quickly and accurately reach a stable state, ultimately 
achieving a stable system. The superiority of fuzzy PID 
controllers over PID control was verified through Simulink 
simulation. Under the action of a fuzzy PID controller, the 
system has fast response speed, short adjustment time, and 
high steady-state accuracy, achieving the expected goals. 
 
REFERENCES 
[1] Hong, J. Research on a Level 1 Linear Inverted Pendulum 
Control System Based on Improved Active Disturbance 
Rejection Control. Anhui University of Engineering, 2019 
[2] Wang, S., Zhang, F., and Chen, Z. Design of LQR controller 
for linear inverted pendulum. Mechanical Manufacturing 
and Automation, 2006, (06): 95-98 
[3] Zhou, M., Miao, X., and Chen, M. Analysis and calibration 
of the control system for a linear inverted pendulum trolley. 
Electronic Testing, 2018, (09): 43-45 
[4] Wang, L., and Kong, Q., Fuzzy PID control of linear 
inverted pendulum. Southern Agricultural Machinery, 2018, 
49 (18): 83-84 
[5] Wang, H., and Kong, Q. Research on PID Control of Linear 
Inverted Pendulum Based on MATLAB. Mechanical 
Engineering and Automation, 2015, (05): 179-180+182 
[6] Chen, C., Zhao, Y., and Gao, J. Comparative analysis of PID 
and LQR control algorithms based on a single inverted 
pendulum. Value Engineering, 2015, 34 (18): 209-2010 
[7] Xu, M., Zhou, B., and Hu, G. Simulation and experimental 
research on the control of a linear inverted pendulum system. 
Machine Tool and Hydraulic, 2018, 46 (06): 90-95. 
[8] Song, S. Research on Optimization of Control Parameters of 
Inverted Pendulum Based on MATLAB. Electronic World, 
2014, (08): 104. 
[9] Luan, H., Sun, D., Sun, H., Sui, Y., and Liu, C. Design of an 
Assistant Teaching Example for Inverted Pendulum Control 
Based on Matlab. Journal of Electrical and Electronics 




---

## 第9页

---

Li et al.                            International Journal of Advanced Engineering Research and Science, 10(12)-2023 
www.ijaers.com                                                                                Page | 9  
Teaching, 2018, 40 (04): 89-93. 
[10] Zhai, L. Establishment of a Simulation Model for a Primary 
Inverted Pendulum. Volkswagen Technology, 2011, (08): 
268-270. 
[11] Ma, C., Hua, Y., and Zhou, L. Comparative Study on 
Control Methods of a Primary Inverted Pendulum. 
Computer Age, 2020, (08): 1-5+9 
[12] Wang, L., Xie, Z., and Wang, Y. Research on Fuzzy 
Adaptive PID Control of Inverted Pendulum Based on 
MATLAB. Mechanical Engineering and Automation, 2020, 
(04): 57-58 
[13] Yue, C. Control and Application of a Class of Nonlinear 
Under actuated Systems. Qingdao University, 2023. DOI: 
10.27262/d. cnki. gqdau. 2022-002274 
[14] Ashwani, K., Pravin, P., Suyashi, R., and Deepak, R. A 
comparison study for control and stabilization of inverted 
pendulum on inclined surface (IPIS) using PID and fuzzy 
controllers. Perspectives in Science, 2016, 8, 187-190. 
[15] Ahmad, I. R., Samer, Y., and Hussain, A. R. Fuzzy-logic 
control of an inverted pendulum on a cart. Computers & 
Electrical Engineering, 2017, 61, 31-47. 
 




---

