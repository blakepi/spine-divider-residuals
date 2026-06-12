# Submission Portal Field Guide

    ## Title

    Residual Limits of a Load-Normalized Spine-Neck Ratio in Compartmental Models

    ## Running title

    Spine-neck load ratio residuals

    ## Abstract

    Dendritic spine-neck resistance is interpretable only relative to the dendritic load it drives. We define equation , where equation is the spine-omitted dendrite-soma input resistance, yielding the DC divider expectation equation . Using SPINE, a transparent Python compartmental implementation, we analyzed residuals between conductance-based peak local transfer and this divider. Across 3718 rows, residuals had median absolute value 0.0548 and maximum 0.492, and were usually negative. Descriptor comparisons showed that SMI is a compact local-transfer coordinate, whereas residuals, head amplitude, and somatic transfer require component resistances, impedance/dynamic descriptors, synaptic conductance scale, active state, and downstream filtering. Deterministic uncertainty stabilized sampled low/intermediate behavior but contained zero high-SMI rows. Independent direct-matrix and DC analytic benchmarks reproduced passive reference behavior to roundoff. SPINE therefore frames spine-neck isolation as an expected divider plus residuals that mark limits of a scalar descriptor.

    ## Keywords

    dendritic spines; compartmental modeling; cable theory; voltage divider; electrical isolation; impedance; reproducible modeling

    ## Authors

    Gregory Pierpoint; Alberto Musto, MD, PhD

    ## Affiliations

    1. Department of Neurology, Macon & Joan Brock Virginia Health Sciences, Eastern Virginia Medical School at Old Dominion University, Norfolk, VA, USA
    2. Department of Biomedical and Translational Sciences, Macon & Joan Brock Virginia Health Sciences, Eastern Virginia Medical School at Old Dominion University, Norfolk, VA, USA

    ## Corresponding author

    Alberto Musto, MD, PhD; mustoae@odu.edu

    ## Funding

    Funding: This work received no external funding.

    ## Competing interests

    The authors declare no competing interests.

    ## Ethics

    This manuscript reports mathematical and computational modeling using repository simulations and no new human participants or animal experiments.

    ## Data availability

    This study uses mathematical and computational modeling and generated no new human participant or animal data. Manuscript-facing derived data, validation outputs, figure/table source data, and provenance ledgers are included in the SPINE release package. Public GitHub URL and Zenodo DOI should be inserted after manual authenticated upload and DOI minting.

    ## Code availability

    The SPINE Python code, configuration files, analysis scripts, tests, validation scripts, environment instructions, and release manifests are included in the approved public-release staging package. Code is released under the MIT License. Derived manuscript-facing data, figures, tables, and documentation are released under CC BY 4.0 unless otherwise stated. Public GitHub URL, release tag/commit, and Zenodo DOI should be inserted after manual authenticated upload and archival integration.

    ## AI disclosure

    Generative-AI tools were used for editorial organization, code-development assistance, revision planning, and manuscript-formatting support. The authors retain responsibility for study conception, model interpretation, validation, numerical verification, reference verification, and final manuscript content. No generative-AI tool is listed as an author.

    ## Author contributions

    Gregory Pierpoint: Methodology; Software; Formal analysis; Investigation; Validation; Visualization; Data curation; Writing - original draft; Writing - review & editing.

    Alberto Musto: Conceptualization; Methodology; Supervision; Project administration; Writing - review & editing; Scientific interpretation; Final manuscript approval.

    ## Suggested reviewers

    Not provided.

    ## Opposed reviewers

    Not provided.

    ## Cover letter

    Dear Editors,
We are pleased to submit "Residual Limits of a Load-Normalized Spine-Neck Ratio in Compartmental Models" as an unblinded Article for consideration in Nature Neuroscience.
This manuscript addresses a basic interpretive problem in dendritic-spine electrophysiology: spine-neck resistance is meaningful only relative to the dendritic load that it drives. We define a load-normalized spine-neck ratio, SMI = R_neck/R_in,d, and use the classical DC voltage divider, Gamma_div = 1/(1+SMI), as an explicit analytic reference rather than as a new law. The scientific contribution is the residual-domain analysis: where transient conductance-based responses depart from this divider, the residuals identify the limits of a single scalar descriptor.
The work should be of interest to Nature Neuroscience readers because spine-neck electrical isolation is often invoked as a mechanistic explanation for synaptic compartmentalization, amplitude amplification, and somatic impact. SPINE separates the local divider expectation from head-amplitude, somatic-transfer, active-state, impedance, and measurement-uncertainty effects, showing where morphology/load shorthand is useful and where richer electrical descriptors are required.
The study uses mathematical and computational modeling only and reports no new human participant or animal experiments. The authors declare no competing interests, and this work received no external funding. A public-release staging repository, final source package, validation outputs, and provenance ledgers have been prepared; authenticated GitHub upload and Zenodo DOI minting remain manual technical steps in the local environment and are documented in the submission package.
All authors approved the submitted manuscript. Correspondence should be addressed to Alberto Musto, MD, PhD (mustoae@odu.edu).
Sincerely,
Gregory Pierpoint
Alberto Musto, MD, PhD
