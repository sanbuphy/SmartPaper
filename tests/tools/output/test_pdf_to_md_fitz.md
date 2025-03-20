## 第1页

---

![《国际高级工程科学与研究》期刊封面](images\page1_img1.png)
> 《国际高级工程科学与研究》期刊封面：这是一张期刊封面，展示了《International Journal of Advanced Engineering Research and Science》的封面设计。包含期刊名称、卷号（Vol-7）、期号（Issue-10）和出版日期（Oct 2020）。封面设计中有多个蓝色多面体图案，以及期刊的DOI和Issue DOI信息。图像的可能用途是作为学术期刊的封面，用于标识和展示期刊信息。

![IAERS期刊标志](images\page1_img2.png)
> IAERS期刊标志：这是一张[标志图]，展示了[International Journal of Advanced Engineering Research and Science（IAERS）的标志]。包含[IAERS的英文缩写和全称]。[标志设计简洁，以蓝色和白色为主，背景为黑色]。图像的可能用途是[作为期刊的标识，用于期刊封面、网站或其他宣传材料中]。

International Journal of Advanced Engineering Research and
Science (IJAERS)
Peer-Reviewed Journal
ISSN: 2349-6495(P) | 2456-1908(O)
Vol-10, Issue-12; Dec, 2023
Journal Home Page Available: https://ijaers.com/
Article DOI:https://dx.doi.org/10.22161/ijaers.1012.1
Study on Control of Inverted Pendulum System Based on
Simulink Simulation
Yongsheng Li, Jiahui Feng, Ruei-Yuan Wang, Ho-Sheng Chen, Yongzhen Gong*
School of Mechanical and Electrical Engineering, Guangdong University of Petrochem Technology (GDUPT), Maoming 525000, China
*Corresponding author
Received: 06 Oct 2023, Abstract— This study aims to conduct control research on an inverted
pendulum system using the Simulink simulation platform. The inverted
Receive in revised form: 10 Nov 2023,
pendulum system is a classic nonlinear dynamic system with important
Accepted: 22 Nov 2023,
theoretical and practical applications. Firstly, establish a mathematical
Available online: 05 Dec 2023
model of the inverted pendulum system, including the dynamic equation of
©2023 The Author(s). Published by AI the pendulum rod and the sensor measurement model. Subsequently, the
Publication. This is an open access article PID (proportional integral differential) controller design method based on
under the CC BY license the inverted pendulum system and the fuzzy PID controller design methods
(https://creativecommons.org/licenses/by/4.0/). were verified through simulation experiments. The ultimate goal is for the
Keywords— Inverted pendulum system, designed fuzzy PID controller to effectively stabilize the inverted pendulum
Proportional integral differential (PID) system in the vertical position and achieve fast tracking of the target
control, Fuzzy PID control, Nonlinear position. Simulation and experimental results show that compared to
dynamic system, Simulink simulation traditional PID controllers, fuzzy PID controllers can quickly stabilize the
pendulum in the target position and have good practicality, stability, speed,
and accuracy. Future research can further explore the application of other
advanced control strategies in inverted pendulum systems, as well as their
potential applications in practical engineering.
I. INTRODUCTION inverted pendulums, planar inverted pendulums, composite
The initial research on inverted pendulums began in inverted pendulums, etc. according to their composition.
the 1950s, designed by control theory experts at the According to their complexity, they can be divided into
Massachusetts Institute of Technology (MIT) in the United primary inverted pendulum systems, secondary inverted
States based on the principle of rocket launch boosters. pendulum systems, tertiary inverted pendulum systems,
The inverted pendulum system, as the model foundation and multi-level inverted pendulum systems. The first-level
for shipborne radar, rocket launch systems, and satellite inverted pendulum system consists of a driving motor, a
attitude control, has been the focus of many researchers in conveyor belt, a pendulum rod, a small car, and a test
the past few decades. The research on inverted pendulums bench [1, 2, 3 ]. The first-level linear inverted pendulum
will tend towards more complex and in-depth studies. system is driven by an electric motor and is an unstable,
Inverted pendulum systems can be divided into linear nonlinear, single-input, double-output, strongly coupled
www.ijaers.com Page | 1



---

## 第2页

---

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
system [4, 5, 6, 14, 15]. It controls both the angle of the established using the Simulink module of MTALAB [9, 10,
pendulum and the position of the trolley to be stable, and 11, 13]. Finally, by comparing and analyzing the curves
the steady-state errors of the trolley position and pendulum and parameters of the established traditional PID controller
angle must be controlled within a small range. and fuzzy PID controller, this study is trying to find out
The control of the inverted pendulum is a difficult whether the fuzzy PID control method is better or not than
point in the study of inverted pendulum control, and there the ordinary PID control method in terms of stability and
have been many studies on the inverted pendulum, which speed.
are basically based on the assumption that the trolley track
of the inverted pendulum system is sufficiently long [7]. II. ESTABLISHING MATHEMATICAL MODEL
With the development of technology, new control methods The working principle of a first-order linear inverted
are constantly emerging, and people use inverted pendulum (Figure 1) is that when the data acquisition card
pendulums to test whether new control methods can transmits the collected data from the rotary encoder to the
handle multivariable, nonlinear, and absolute instability. computer and compares it with the set value. The deviation
The inverted pendulum has become an ideal experimental is processed through some calculation, and a control law is
method for testing the effectiveness of control strategies issued to control the motor to make the pendulum swing
[8]. This article focuses on a first-order inverted pendulum left and right into the stable range, thereby achieving the
system. Firstly, a mathematical model is established using pendulum to stand upright and not fall, as well as
the knowledge of Newtonian mechanics, and then a self-swing [12].
simulation model of the inverted pendulum system is
Fig.1 Working Principle Diagram of a First Level Linear Inverted Pendulum
Because establishing a mathematical model of the coefficient of the car rf =0.1N/m/sec, the inertia of the
system is the foundation for studying control methods, the swing rod I=0.0034kg*m2, and the gravitational
first step is to model the inverted pendulum system in this acceleration g=9.8N/ m2. The physical model diagram of
paper. And mathematical modeling is carried out using the the inverted pendulum system is shown in Figure 2. A
Newtonian mechanics method to obtain the state-space detailed decomposition of various forces acting on the
equation of the system and prepare for the subsequent pendulum and trolley using Newtonian mechanics
controller design and simulation. methods is shown in Figure 3. P and N are set as the
The model parameters of the inverted pendulum components of the interaction force in the vertical and
system are the pendulum mass m =0.109kg, the trolley horizontal directions during the movement or stability of
1
mass m =1.096kg g, the angle between the pendulum and the car.
2
the vertical direction θ (rad), the distance from the center
of the swing rod to the car l=0.25m, the distance the car
moves x (m), the force applied to the car f (N), the friction
www.ijaers.com Page | 2



---

## 第3页

---

![汽车摆杆系统动力学模型](images\page3_img1.png)
> 汽车摆杆系统动力学模型：这是一张示意图，展示了汽车与摆杆系统的动力学模型。包含汽车质量m2、摆杆长度2l、摆杆与垂直方向的夹角φ、作用在汽车上的力F以及汽车的位移xc和速度r1x。图中标注了“swing rod”和“car”，并显示了力和位移的方向。图像可能用于解释汽车与摆杆系统在动力学分析中的相互作用。

![斜面力学受力分析图](images\page3_img2.png)
> 斜面力学受力分析图：这是一张示意图，展示了物体在斜面上的受力分析。包含重力（m1g）、法向力（N）、切向力（P）以及角度θ和φ。图中标注了力的方向和角度关系。图像可能用于物理教学或力学分析中，解释物体在斜面上的运动和受力情况。

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
Set angle θ= π+ φ， and φ after being converted to radians,
it is much less than 1 rad, that is φ≪1. So it can be
simplified as cos𝜃 =−1, and sin𝜃
=−𝜑，(𝑑𝜃 )2
=0.
𝑑𝑡
Using u instead of the input force F, equations (3) and (6)
can be simplified as:
(I+𝑚 𝑙2)𝜑̈ −𝑚 g𝑙𝜑=̇ 𝑚 𝑙𝑥̈
{ 1 1 1
(𝑚 +𝑚)𝑥̈ +𝑟 𝑥̇ −𝑚 𝑙𝜑̈ =𝑢
2 𝑓 1
(7)
Fig.2 Physical Model of Inverted Pendulum System
Perform a Laplace transform on the above equation, which
will be
(I+𝑚 𝑙2)Φ(𝑠)𝑠2−𝑚 g𝑙Φ(𝑠)=𝑚 𝑙Χ(𝑠)𝑠2
{ 1 1 1
(𝑚 +𝑚)Χ(𝑠)𝑠2+𝑟 Χ(𝑠)𝑠 −𝑚 𝑙Φ(𝑠)𝑠2 =𝑈(𝑆)
2 𝑓 1
(8)
The first equation in the above equation can be written as
follows:
Φ(𝑆)
=
𝑚1𝑙𝑠2
(9)
𝑋(𝑆) (𝐼+𝑚1𝑙2)−𝑚1g𝑙
Substitute equation (9) into the equation with the control
input in equation (8), which will be
Fig.3 Force Analysis Diagram of the Small Car and
𝜙(𝑆)
=
Swing Rod
𝑈(𝑆)
𝑚 𝑤1𝑙 𝑠2
𝑠4+𝑟 𝑓(𝐼+𝑚1𝑙2) 𝑠3−(𝑚1+𝑚2)𝑚1g𝑙 𝑠2−𝑟𝑓𝑚1g𝑙
𝑠
𝑤 𝑤 𝑤
According to Figure 3, first analyze the force in the
(10)
horizontal direction. wherein，w=[(𝑚 +𝑚 )(𝐼+𝑚 𝑙2)−(𝑚 𝑙)2]。
1 2 1 1
𝑚 𝑥̈ =𝐹−𝑟 𝑥̇ −𝑁 (1) Using equation (7) for 𝑥̈ and𝜑̈ solve, which will be
2 𝑓
N=𝑚
𝑑2
(𝑥+𝑙sin𝜃)=𝑚 𝑥̈ +𝑚 𝑙𝜃̈cos𝜃−
𝑥̇ =𝑥̈
1𝑑𝑡2 1 1
𝑚 𝑙𝜃2̇ sin𝜃 (2) 𝑥̈ =
−(𝐼+𝑚1𝑙2)𝑟𝑓
𝑥̇ +
𝑚12g𝑙2
𝜑+
(𝐼+𝑚1𝑙2)
𝑢
1 (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 (𝑚1+𝑚2 )𝐼+𝑚1𝑚2𝑙2 (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
Substituting equation (2) into equation (1) yields the
𝜑̇ =𝜑̈
equation of motion in the horizontal direction
(𝑚 1+𝑚 2)𝑥̈ +𝑟 𝑓𝑥̇ +𝑚 1𝑙𝜃̈cos𝜃−𝑚 1𝑙𝜃2̇ sin𝜃 = 𝜑̈ = 𝑚1𝑙𝑟𝑓 𝑥̇ + 𝑚1g𝑙(𝑚1+𝑚2) 𝜑+ 𝑚1𝑙 𝑢
{ (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 (𝑚1+𝑚2 )𝐼+𝑚1𝑚2𝑙2 (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
𝐹 (3)
In the vertical direction, as the car is used as the horizontal (11)
Compiled into a standard state space equation as
plane, only the force acting on the swing rod needs to be
analyzed to obtain
0 1 0 0
P−𝑚 1g=𝑚 1𝑑𝑑 𝑡2 2(𝑙cos𝜃)=−𝑚 1𝑙𝜃̈sin𝜃− [𝑥 𝑥̇ ̈
]=
0 (𝑚1− +( 𝑚𝐼+ 2𝑚 )𝐼1 +𝑙 𝑚2) 1𝑟 𝑚𝑓 2𝑙2 (𝑚1+𝑚𝑚 21 )2 𝐼+g𝑙 𝑚2 1𝑚2𝑙2 0 [𝑥 𝑥̇
]+
𝜑̇ 0 0 0 1 𝜑
𝑚 1𝑙𝜃̈sin𝜃−𝑚 1𝑙𝜃̇2cos𝜃 (4) 𝜑̈
0
𝑚1𝑙𝑟𝑓 𝑚1g𝑙(𝑚1+𝑚2)
0
𝜑̇
The torque balance equation is [ (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2 ]
0
−P𝑙sin𝜃−𝑁𝑙cos𝜃 =I𝜃̈ (5) (𝐼+𝑚1𝑙2)
The second equation of motion can be obtained by using (𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2
𝑢 (12)
0
equations (2) and (4)
𝑚1𝑙
(I+𝑚 1𝑙2)𝜑̈ −𝑚 1g𝑙𝜑̇ =𝑚 1𝑙𝑥̈ (6) [(𝑚1+𝑚2)𝐼+𝑚1𝑚2𝑙2]
www.ijaers.com Page | 3



---

## 第4页

---

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
𝑥
and simulate it using Simulink in Matlab. We then adjust a
𝑥 1 0 0 0 𝑥̇
y=[ ]=[ ][ ] suitable set of PID parameters through parameter tuning
𝜃 0 0 1 0 𝜑
𝜑̇ principles. The input is the unit step signal, and the PID
If the pendulum is regarded as a rod with uniform mass, parameter is K = 70, K = 0.7, K = 6 the system reaches
p I D
then the inertia of the pendulum is
steady state at time T=0.08S.
I=1 𝑚 𝑙2 (13) The fuzzy controller designed here is a two-input,
3 1
three-output fuzzy PID controller, and the two output
Substituting equation (13) into the first equation of
equation (7) yields signals jointly use a fuzzy rule. The input is the error e=
(1 𝑚 𝑙2+𝑚 𝑙2)𝜑̈ −𝑚 g𝑙𝜑̇ =𝑚 𝑙𝑥̈ (14) r(k)-y(k) and error change rate ec = e(k)-e(k-1) between
3 1 1 1 1
Simplify the above equation, which will be the given value and the actual value of the car
3g 3
𝜑̈ = 𝜑+ 𝑥̈ (15) displacement or swing rod angle, and the output is the
4𝑙 4𝑙
Let the system s tate space equation be
corrected values ΔK , ΔK, andΔK of the PID parameters.
′ p I D
𝑋̇ =𝐴𝑋+𝐵𝑢
{ (16) In this design, the basic domain of error e is taken as
𝑌 =𝐶𝑋+𝐷𝑈
' [-5, 5], and the basic domain of error change rate ec is
Let X=[𝑥̇ 𝑥̈ 𝜃̇ 𝜃̈], u = ẍ，The following state
space expression can be obtained taken as [-5, 5]. The domain of the output variablesΔK p,
ΔK, andΔK are taken as [-3, 3].
𝑥̇ 0 1 0 0 𝑥 0 I D
𝑥̈ 0 0 0 0 𝑥̇ 1 In order to obtain the input of the fuzzy controller, it
[ 𝜑̇]= 0 0 0 1 [ 𝜑]+ 0 𝑢′ (17)
is necessary to fuzzify the precise quantity, that is,
3g 3
𝜑̈ [0 0 0 ] 𝜑̇ [ ]
4𝑙 4𝑙 multiply the input quantity by the corresponding
𝑥 quantization factor, and convert it from the basic domain
𝑥 1 0 0 0 𝑥̇
Y=[ ]=[ ][ ] to the corresponding fuzzy domain. The quantization
𝜃 0 0 1 0 𝜑
𝜑̇ factor of error e isα e=0.8, and the factor of error change
rate ec is α ec=0.2. The control quantity obtained through
III. CONTROLLER DESIGN AND FUZZY LOGIC the fuzzy control algorithm is a fuzzy quantity that needs
ESTABLISHMENT to be multiplied by a proportional factor and converted
Firstly, traditional PID is used to design PID into the basic domain. When the output variable is the
controllers for the output displacement and output angle of displacement of the car, the scaling factor ofΔK p,ΔK I,ΔK D
the system. Through parameter tuning and control, the areα ΔKp =α ΔKI =1,α ΔKD =-5. When taking the output variable
spatial-state equation output reaches a stable state. When swing angle, the scaling factor of ΔK p,ΔK I,ΔK D
studying the displacement of a small car, the spatial state areα ΔKp=200,α ΔKI=1,α ΔKD=30
control equation of the system is obtained by inputting the Divide the fuzzy domain of input variables(e, ec) and
car parameters into equation (17) as follows: output variables (ΔK p,ΔK I,ΔK D) into 7 fuzzy subsets,
0 1 0 0 0 namely NB, NM, NS, ZO, PS, PM, PB representing
𝑋
=[0 0 0 0
]𝑋+[
1 ]𝑢′
negative big, negative medium, negative small, zero,
0 0 0 1 0
(18) positive small, positive medium, and positive big,
0 0 0 29.4 0.75
respectively. The membership functions of input variables
{ Y=[𝑥]=[1 0 0 0]𝑋 and output variables both adopt triangular membership
We first use the traditional PID control method to functions, as shown in Figure 4.
control the spatial-state equation of displacement output
www.ijaers.com Page | 4



---

## 第5页

---

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
Fig.4 The Membership Function of e, ec,ΔK ,ΔK,ΔK
p I D
The fuzzy rule statement used by the output variable fuzzy controller is as follows:
“if E isαand EC isβthen U isγ” Wherein,α,β,γboth represent the fuzzy sets corresponding to each variable.
Based on the impact of PID parameters on system performance, parameter tuning principles, expert experience, and
cognition, 49 control rules were obtained after processing, as shown in Tables 1–3.
Table 1 Fuzzy Rule Table ofΔK
p
𝐾 E
𝑃
NB NM NS O PS PM PB
EC
NB PB PB PB PB PM PS O
NM PB PB PB PB PM O O
NS PM PM PM PM O PS PS
O PM PM PS O NS NS NM
PS PS PS O NS NM NM NM
PM PS O NS NM NM NM NB
PB O O NM NM NM NB NB
Table 2 Fuzzy Rule Table ofΔK
I
E
𝐾
𝐼
NB NM NS O PS PM PB
EC
NB NB NB NM NM NS O O
NM NB NB NM NS NS O O
NS NB NM NS NS O PS PS
O NM NM NS O PS PM PM
PS NM NS O PS PS PM PB
PM O O PS NM PM PB PB
PB O O PS PM PM PB PB
www.ijaers.com Page | 5



---

## 第6页

---

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
Table 3 Fuzzy Rule Table ofΔK
D
E
𝐾
𝐷
NB NM NS O PS PM PB
EC
NB PS NS NB NB NB NM PS
NM PS NS NB NM NM NS O
NS O NS NM NM NM NS O
O O NS NS NS NS NS O
PS O O O O O O O
PM PB PS PS PS PS PS PB
PB PB PM PM PM PS PS PB
This design system uses the Mamdani inference parameters of the PID controller.
method to perform fuzzy inference on the established 𝐾 =𝐾 + △𝐾 (19)
𝑃 𝑃0 𝑃
fuzzy rules in order to obtain control variables. Meanwhile, 𝐾 =𝐾 + △𝐾 (20)
𝐼 𝐼0 𝐼
using the center of gravity method to solve the fuzziness of 𝐾 =𝐾 + △𝐾 (21)
𝐷 𝐷0 𝐷
language expression, thus obtaining the exact value
ofΔK ,ΔK,ΔK . In addition, the values obtained through Before establishing a fuzzy logic controller, the Tool
p I D
fuzzy reasoning and deblurring are multiplied by the Box parameters of the fuzzy logic system need to be set in
corresponding scaling factors to obtain the incremental Simulink (Figure 5). Then use the membership function
adjustment values of PID parameters, which are then parameter setting process of Tool Box (Figure 6) to
substituted into equations (19) - (21) to obtain the control establish the membership function of e, ec,ΔK ,ΔK,ΔK .
p I D
Fig.5 Fuzzy Logic System Tool Box
www.ijaers.com Page | 6



---

## 第7页

---

![Simulink模糊PID控制系统](images\page7_img2.png)
> Simulink模糊PID控制系统：这是一张[示意图]，展示了[一个控制系统的Simulink模型]。包含[多个模块和信号流]，如Step输入、Gain模块、Integrator、Derivative、State-Space模块以及Fuzzy PID控制器。[文本标签包括Step4、Sum3、Gain11、Gain12、Gain13、Integrator1、Derivative2、State-Space4、State-Space5、Fuzzy pid2等]。图像的可能用途是[用于解释和设计复杂的控制策略，特别是结合传统PID控制和模糊逻辑控制的系统]。

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
Fig.6 Membership Function of Fuzzy Logic System
After setting the above parameters, they can be traditional PID controllers have good control effects on the
added to the rule editor, and all output surfaces of the control object that can assume an accurate mathematical
fuzzy inference system can be observed in the output model. They can meet the requirements of system control
surface observer. accuracy and rise time, but there are problems such as long
adjustment times. The fuzzy PID controller can adjust the
IV. COMPARISON BETWEEN TRADITIONAL PID parameters of the system in real time. By doing so, the
PID CONTROL AND FUZZY PID CONTROL PID parameters can be more suitable for the control
Through Simulink simulation (Figure 7 and Figure requirements of the system, resulting in better control
8), it was found that, under appropriate parameters, effects than traditional PID controllers (Figure 9).
Fig.7 Simulink Simulations of Traditional PID and Fuzzy PID Control Systems (Swing Angle)
www.ijaers.com Page | 7



---

## 第8页

---

![模糊逻辑控制信号流程图](images\page8_img1.png)
> 模糊逻辑控制信号流程图：这是一张示意图，展示了控制系统中的信号处理流程。包含多个模块如增益（Gain）、积分器（Integrator）、模糊逻辑控制器（Fuzzy Logic Controller）和加法器（Add）。文本标签包括“E”、“Derivative”、“Fuzzy Logic Controller1”、“Out1”等。图像可能用于解释复杂控制系统的设计和信号流，特别是涉及模糊逻辑控制和PID控制的场景。

![PID与模糊PID控制对比](images\page8_img2.png)
> PID与模糊PID控制对比：这是一张[图表]，展示了[传统PID控制和模糊PID控制的仿真对比]。包含[两条曲线分别代表PID控制器和模糊PID控制器的响应，以及时间轴和响应值轴]。[图中显示模糊PID控制器的响应更快，且在0.1秒内趋于稳定，而传统PID控制器有轻微的超调和振荡]。图像的可能用途是[用于分析和比较不同控制策略的性能，特别是在快速响应和稳定性方面]。

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
Fig.8 Simulink Simulation of a Fuzzy PID Controller for Swing Angle
Fig.9 Response Curves of Traditional PID and Fuzzy PID Controller Systems (Swing Angle)
V. CONCLUSIONS [2] Wang, S., Zhang, F., and Chen, Z. Design of LQR controller
The inherent first-order linear inverted pendulum for linear inverted pendulum. Mechanical Manufacturing
system is a typical single-input, multiple-output nonlinear and Automation, 2006, (06): 95-98
system. This article analyzes the motion of the inherent [3] Zhou, M., Miao, X., and Chen, M. Analysis and calibration
first-order linear inverted pendulum system, establishes a of the control system for a linear inverted pendulum trolley.
mathematical model of the first-order linear inverted Electronic Testing, 2018, (09): 43-45
pendulum system using the Newtonian mechanics method, [4] Wang, L., and Kong, Q., Fuzzy PID control of linear
and designs PID controllers and fuzzy PID controllers to inverted pendulum. Southern Agricultural Machinery, 2018,
control the first-order linear inverted pendulum system 49 (18): 83-84
separately. [5] Wang, H., and Kong, Q. Research on PID Control of Linear
By adjusting their proportional constant and integral Inverted Pendulum Based on MATLAB. Mechanical
constant, the three parameters of the differential constant Engineering and Automation, 2015, (05): 179-180+182
enable the first-order linear inverted pendulum system to [6] Chen, C., Zhao, Y., and Gao, J. Comparative analysis of PID
quickly and accurately reach a stable state, ultimately and LQR control algorithms based on a single inverted
achieving a stable system. The superiority of fuzzy PID pendulum. Value Engineering, 2015, 34 (18): 209-2010
controllers over PID control was verified through Simulink [7] Xu, M., Zhou, B., and Hu, G. Simulation and experimental
simulation. Under the action of a fuzzy PID controller, the research on the control of a linear inverted pendulum system.
system has fast response speed, short adjustment time, and Machine Tool and Hydraulic, 2018, 46 (06): 90-95.
high steady-state accuracy, achieving the expected goals. [8] Song, S. Research on Optimization of Control Parameters of
Inverted Pendulum Based on MATLAB. Electronic World,
REFERENCES 2014, (08): 104.
[1] Hong, J. Research on a Level 1 Linear Inverted Pendulum [9] Luan, H., Sun, D., Sun, H., Sui, Y., and Liu, C. Design of an
Control System Based on Improved Active Disturbance Assistant Teaching Example for Inverted Pendulum Control
Rejection Control. Anhui University of Engineering, 2019 Based on Matlab. Journal of Electrical and Electronics
www.ijaers.com Page | 8



---

## 第9页

---

Li et al. International Journal of Advanced Engineering Research and Science, 10(12)-2023
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
www.ijaers.com Page | 9



---

