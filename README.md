# cell-kn-mvp

Welcome to the repository tracking issues with the NLM Cell Knowledge Network Minimum Viable Product.
The mission of this product is to create the specifications for an application to be proposed to be added to the official National Library of Medicine web site.

This application creates a knowledge network encapsulating the latest knowledge on cells, the evidence primarily coming from single cell RNA-sequencing experiments, including but not limited single nucleus as well as single cell RNA-sequencing experiments, spatial cell RNA-sequencing experiments.  The majority of these data and those stored within many repositories, notably the chan-zuckerburg [cellxgene](https://cellxgene.cziscience.com/).  Many of these data the foundations for numerous cell atlases.

The NLM Cell Knowledge Network aims to connect this experiment data and augment it with marker data computationally derived from exeuction of the [NSForest](https://github.com/JCVenterInstitute/NSForest/tree/master) program which calculates both the necessary and sufficient genes that when present define the cell cluster, resolved to a cell ontological type using semantic terms updated and maintained at the [Cell Ontology](https://www.ebi.ac.uk/ols4/ontologies/cl) 


## Cloning a private repository

Due to Executive Orders regarding communication, this repository is at this time private, requiring users to authenticate when cloning the repository.

When cloning, one typically does this from a command shell.  Best done in a clean environment, you need to install GitHub command line tool to authenticate from the command line.

Visiting Anaconda Packages Repository, you can search for [gh](https://anaconda.org/conda-forge/gh) the command line GitHub authentication (and other functions) tool.

### Step 1 - create a new environment

Leave an old environment and start anew.

```bash
conda deactivate
conda create -n cell -y
```

This creates a clean slate for you to begin your work - so now you activate it so you are within this clean environment.
```bash
conda activate cell
```

### Step 2 -- clone the repository

 Now you want to clone - typically one uses the **`https`** and it is convenient to just select **`copy`** to get the command.
 
```bash
git clone https://github.com/NIH-NLM/cell-kn-mvp.git
Cloning into 'cell-kn-mvp'...
remote: The 'NIH-NLM' organization has enabled or enforced SAML SSO.
remote: To access this repository, visit https://github.com/orgs/NIH-NLM/sso?authorization_request=AA2ART22DSJUEVNRUN4BORLHUUYAXA5PN5ZGOYLONF5GC5DJN5XF62LEZYFE2E7PVVRXEZLEMVXHI2LBNRPWSZGOKP6C7EFPMNZGKZDFNZ2GSYLML52HS4DFVNHWC5LUNBAWGY3FONZQ and try your request again.
fatal: unable to access 'https://github.com/NIH-NLM/cell-kn-mvp.git/': The requested URL returned error: 403
```

Oh my!  That's right we are private, but following the instructions we find we can be authenticated

Once authenticated you can try again
```
(cell) (env) adeslatt@Annes-MacBook-Pro projects % git clone https://github.com/NIH-NLM/cell-kn-mvp.git
Cloning into 'cell-kn-mvp'...
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (11/11), done.
remote: Total 15 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (15/15), done.
```

All is well!

