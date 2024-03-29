I have dedicated many volunteer hours toward helping voters make an informed vote by providing them with information beyond what is on the ballot. During a research class in my data science master’s program, I had the opportunity to conduct a small experiment to answer the question of whether additional information provided to voters would affect their level of support for a given ballot measure. The research concept was my own and I conducted the experiment and analysis with two classmates. The code shared here is my own. The paper was written jointly with my classmates.

We used the actual ballot language for three ballot measures from a recent statewide California election. The control group was provided with just the ballot language and the treatment group was given lists of financial contributors and endorsers both for and against each ballot measure. A screenshot of the survey question for one of the ballot measures in the treatment condition can be seen below. Respondents were given a slider to select their level of support or opposition for the measure.

![Ballot-Language_treatment](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/AmbulanceTreatmentWithSlider.png)

We were limited in time and resources, but managed to collect several hundred survey responses. We used regression models (in R) to assess whether additional information affected the voter’s level of support for each ballot measure and controlled for covariates including education level, income, political party, intensity of party affiliation, and voting habits. A covariance balance check confirmed that respondents in each covariate group were evenly distributed between the treatment and control groups and thus, the covariates would not influence the treatment effect.

![Covariate-Balance](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/CovariateBalance.png)

Our analysis appeared to confirm the assumption that political party and the intensity of party affiliation were strong predictors of support for the measures, but this was not the question we set out to answer. There was a small difference in the level of support of ballot measures for voters receiving additional information. Unfortunately, because of the small sample size, our experiment was underpowered and the treatment effect was statistically insignificant.

![distribution-of-support](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/DistributionOfSupport.png)

We had conducted a small pilot study to determine a target number of participants to reach an 80% power threshold, but because our pilot was so small, the predictions ended up being too low. 

![power-estimates](https://github.com/lplimier/Data_Science_Portfolio/blob/master/Images/power_estimates.png)

The dotted lines of the graph above show the predicted power curve based on the pilot study. The solid lines in graph show predicted power curve for our final experiment. The left-hand column of dots shows the actual power for the pilot study and the right hand column of dots are the actual power numbers, which are lower than the predicted power curve because of a treatment/control imbalance. In an ideal world, we would use the full experiment as a robust pilot and target a much larger, more diverse audience for a final study.
