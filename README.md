# probCOmp
Probabilistic method to compare ceramic chaînes opératoires.

## Introduction

## How to use


## Note on random path generation
The procedure for random path generation in this script differs from 
that described in Kroon (2024, Appendix F), and this difference leads 
to an increase in the average length of randomly generated paths.

The script in Kroon (2024, Appendix F) contains a check which 
terminates and discards a random path if the next node selected for the 
path has already been visited in the path (loop prevention). This check 
likely selects against long paths, since a newly selected node is more 
likely to have been visited previously the longer the path.

In this script, a check is applied prior to the selection of a new node 
which removes all nodes featuring on a path from the pool of potential 
new nodes. The result is a more efficient path generation process, but 
also an increase in average path length from 11 to 18 (calculated over 
1,000 paths).

## How to cite
Please refer to this GitHub repository, and Kroon (2024, Appendix F) 
when using this script.

## Sources
Hagberg, A.A., D.A. Schult, and P.J. Swart, 2008. Exploring network 
structure, dynamics, and function using NetworkX”. In: G. Varoquaux, T. 
Vaught, and J. Millman (eds). *Proceedings of the 7th Python in Science* 
*Conference (SciPy2008)*. Pasadena (CA): SciPy (SciPy Proceedings 11), 
pp. 11–15. DOI: [text](https://doi.org/10.25080/TCWV9851)

Kroon, E.J., 2024. *Serial Learners: Interactions between Funnel Beaker* 
*West and Corded Ware Communities in the Netherlands during the Third* 
*Millennium BCE from the Perspective of Ceramic Technology*. Leiden: 
Sidestone Press. DOI: [text](https://doi.org/10.59641/4e367hq)

Roux, V., 2019. *Ceramics and Society*. Cham: Springer International 
Publishing. DOI: [text](https://doi.org/10.1007/978-3-030-03973-8)

Virtanen, P., R. Gommers, T. E. Oliphant, M. Haberland, T. Reddy, D. 
Cournapeau, E. Burovski, P. Peterson, W. Weckesser, J. Bright, S. J. 
van der Walt, M. Brett, J. Wilson, K. J. Millman, N. Mayorov, A. R. J. 
Nelson, E. Jones, R. Kern, E. Larson, C. J. Carey, İ. Polat, Y. Feng, 
E. W. Moore, J. VanderPlas, D. Laxalde, J. Perktold, R. Cimrman, I. 
Henriksen, E. A. Quintero, C. R. Harris, A. M. Archibald, A. H. 
Ribeiro, F. Pedregosa, P. van Mulbregt, SciPy 1.0 Contributors, (2020). 
SciPy 1.0: Fundamental algorithms for scientific computing in Python. 
*Nature Methods*, 17(3), 261-272. DOI: 
[text](https://doi.org/10.1038/s41592-019-0686-2)

## Acknowledgements
I thank the following colleagues for the feedback and suggestions while 
developping the original script: P. Dionigi, D. Garlaschelli, W.Th.F. 
den Hollander, Q.P.J. Bourgeois. All remaining errors are my own.
