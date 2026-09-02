# Unverified References

Per this audit's directive: for every reference that supports a substantive
scientific claim, its bibliographic metadata must either be independently
verified, or flagged rather than trusted on faith. This document flags what
could not be independently verified in this session.

**Environment constraint, stated plainly:** this session's `WebFetch` tool
returns `EGRESS_BLOCKED` for essentially all external domains (Google
Scholar, publisher sites, DOI resolvers, arXiv, PMC, IEEE Xplore). This is a
network-policy restriction of the sandboxed environment this audit runs in,
not a judgment that these sources don't exist. It means: independent
re-verification of the entries below was not possible in this session, and
per this audit's own rule, that must be disclosed rather than papered over.

**I cannot provide independent re-verification for the sources listed below
from this session's tools without risking a hallucination.** Each entry's
bibliographic metadata (author, title, venue, year) was located via a
targeted live search when it was first added to this bibliography and is
believed accurate on that basis, but was not independently re-confirmed by
fetching the source itself in this audit pass. This is exactly the `[S]`
tier already disclosed in `references.bib`'s own section comments and in
the manuscript's "Literature Verification Note" (`sec:related`) --- this
document is a formal, complete enumeration of that same disclosed set, not
a new finding.

## Methodology

1. Extracted all 114 bibliography entries tiered `[S]` in
   `references.bib`'s own section-comment markers (as opposed to `[V]`,
   independently fetched/confirmed, or `[STD]`, a standards document with
   institutional rather than authorial provenance).
2. Cross-referenced each against `research/claim_citation_matrix.csv`
   (Phase 3) to find the exact manuscript sentence(s) it supports.
3. Scanned every `[S]`-tier-supported claim for unhedged strong language
   ("proves," "guarantees," "definitively," etc.) that would indicate the
   manuscript is treating an unverified source as settled fact rather than
   a disclosed, partial-confidence citation. **One row matched** (see
   "Individually reviewed entries" below); on inspection, the manuscript
   already discloses and hedges it more thoroughly than anywhere else in
   the paper, so no change was needed.
4. Separately checked bibliographic field completeness (Phase 15 of the
   prior audit, reconfirmed in `research/citation_integrity_report.md`):
   two entries are missing a `year` field.

## Disposition key

- **A** --- remove the claim (not applicable to any entry below: no claim
  in this manuscript rests *solely* and *load-bearingly* on an unverifiable
  source without independent corroboration or explicit hedging, except the
  one flagged individually below, which is already handled by the
  manuscript's own explicit hedging).
- **B** --- rewrite as an uncited observation (not applied: every claim
  below is specifically attributable to its source, not a general
  background assertion masquerading as sourced).
- **C** --- support with another verified source instead (not applied: no
  `[V]`-tier substitute exists for these specific claims in this project's
  current reference collection; substituting an unrelated `[V]` source
  just to upgrade a tier label would itself be a form of citation
  misrepresentation).
- **D** --- explicitly mark as a disclosed assumption/partial-confidence
  citation. **This is the disposition for all 114 entries below.** It is
  not a default applied without basis: it is what the manuscript's own
  pre-existing tiering system and "Literature Verification Note" already
  do for every one of these entries, confirmed here as still accurate and
  still in force. Two entries additionally get individual treatment below
  because they raised a distinct issue (field completeness / an internal
  date conflict) beyond the general tiering disclosure.

## Individually reviewed entries

**`atutxasanz2025authentication`** --- the one claim row matching the
strong-language scan (the word "guarantee," in "QKD's classical control
channel ... is itself the trust anchor for QKD's entire security
guarantee"). On inspection, "guarantee" here refers to QKD's standard,
textbook information-theoretic security property, not a claim about this
paper's own contribution. More importantly, the manuscript already singles
out this exact dependency as its single most consequential unverified
assumption, stating directly (Security Considerations,
`sec:security`/Residual Risk Summary): *"if the specific claim in
[this source] ... does not hold up under independent verification ...,
this paper's QKD security guarantee is undermined at its foundation, not
merely weakened --- this is the single highest-leverage unverified claim
in the entire paper."* This is Disposition D already applied by the
manuscript itself, at a higher level of explicitness than this audit would
have added. No change made.

**`aguilarmelchor2018hqc`** and **`etsi2018whitepaper27`** --- both missing
a `year` field (see `research/citation_integrity_report.md` for full
detail). For `aguilarmelchor2018hqc` specifically, the entry carries an
unresolved internal conflict: its key encodes "2018," but its arXiv
identifier (`1612.05572`) encodes December 2016. Inserting either year
without independently confirming which corresponds to which
publication venue would itself be the exact fabrication this audit exists
to prevent, so neither was inserted. **Disposition D, with an explicit
caveat**: both entries' underlying claims (HQC's NIST selection; ETSI's
publication of a QKD security assessment) do not depend on the exact
year and are independently corroborated by other cited sources
(`nist2025pqcround4status` for the HQC selection claim), so no manuscript
prose required change --- but the bibliography entries themselves should
be corrected by the authors once external verification access is
available, rather than left permanently incomplete.

## Full enumeration (114 entries)

| Citation key | Example supported claim (from claim-citation matrix) | Disposition |
|---|---|---|
| `aguilarmelchor2018hqc` | Beyond the lattice family, NIST's fourth standardization round selected HQC, a code-based KEM built on the syndrome-decoding problem~, as... | D |
| `alif2024healthcareiot` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `anon2026securemedical` | A further set of sources --- --- were located via live web search with real, specific titles, authors (where available), and venues ident... | D |
| `atutxasanz2025authentication` | Third, and most directly relevant to this paper's central mechanism, QKD's classical control channel --- which carries the sifting, error... | D |
| `automotiveikev2hybrid2026` | Beyond DNS, PQC overhead has been measured in IPsec directly~, in IKEv2 specifically under constrained and Internet-scale network conditi... | D |
| `bedgehealth2021` | Beyond the wireless-security literature specifically, PQC integration into mobile-network resilience more broadly is an active area~, and... | D |
| `bennett1984bb84` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `bernstein2019sphincsplus` | NIST selected two further signature schemes alongside ML-DSA for standardization diversity: FALCON, a compact NTRU-lattice-based scheme t... | D |
| `bestofbothkems2025` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `bikesuite2024spec` | Beyond the lattice family, NIST's fourth standardization round selected HQC, a code-based KEM built on the syndrome-decoding problem~, as... | D |
| `blockchainlatticeehr2025` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `blockchainquantumehealth2025` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `bos2018kyber` | The NIST post-quantum cryptography standardization process selected ML-KEM (based on the Module Learning-With-Errors problem over a struc... | D |
| `chen2025tls13hybrid` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `clason2026deployed` | QKD is real and field-deployed --- a 300\,km trusted-node network has been reported in operation~ --- but it is also a bounded, rate-limi... | D |
| `combinedqpq2025finitekeys` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `compactdilithiumm3m42020` | The pqm4 benchmarking framework for NIST PQC algorithms on ARM Cortex-M4 microcontrollers~, and its subsequent extension to additional po... | D |
| `corednspqc2025` | Independent of Goertzen and Stebila's DNSSEC fragmentation proposal, a real post-quantum DNSSEC implementation in the CoreDNS server has ... | D |
| `deployinghybrid2023` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `dervisevic2024qkdkeymgmt` | This pool-and-buffer abstraction is consistent with how the QKD-networking literature itself generally treats key management: a recent su... | D |
| `desattackerinteraction2015` | Discrete-event simulation is an established methodology for evaluating security-system behavior specifically, not merely general system p... | D |
| `despowergridrisk2024` | Discrete-event simulation is an established methodology for evaluating security-system behavior specifically, not merely general system p... | D |
| `dnssystemstudy2025` | Independent of Goertzen and Stebila's DNSSEC fragmentation proposal, a real post-quantum DNSSEC implementation in the CoreDNS server has ... | D |
| `ducas2018dilithium` | The NIST post-quantum cryptography standardization process selected ML-KEM (based on the Module Learning-With-Errors problem over a struc... | D |
| `edgenativefederatediomt2026` | An edge-native federated-learning approach to securing IoMT in the post-quantum era~ is architecturally close to this paper's own edge-ga... | D |
| `embeddedpqccomplexity2025` | More recent surveys and comparative studies address the complexity and optimization strategies PQC requires specifically in embedded cont... | D |
| `etsi2018whitepaper27` | This is not a universally shared institutional position --- the European Telecommunications Standards Institute has published its own tec... | D |
| `euroqci2026shield` | This is not a universally shared institutional position --- the European Telecommunications Standards Institute has published its own tec... | D |
| `euroqci2026sizing` | This is not a universally shared institutional position --- the European Telecommunications Standards Institute has published its own tec... | D |
| `fasterkyberdilithiumm42022` | The pqm4 benchmarking framework for NIST PQC algorithms on ARM Cortex-M4 microcontrollers~, and its subsequent extension to additional po... | D |
| `financialquantumsafe2025` | Closer to this paper's own domain analogy, adaptive and QKD-aware mechanisms have also been proposed for other critical-infrastructure se... | D |
| `focombiners2021` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `forecastingqctimelines2020` | Expert-survey-based CRQC timeline estimates are updated periodically; the Global Risk Institute's most recent annual survey of quantum-co... | D |
| `fouque2020falcon` | NIST selected two further signature schemes alongside ML-DSA for standardization diversity: FALCON, a compact NTRU-lattice-based scheme t... | D |
| `garms2024hybridqkdpqc` | The formal security analysis itself is addressed directly by two independent treatments of KEM-combiner security~ and by a formal random-... | D |
| `grassl2016groveraes` | Grover's algorithm gives a quantum adversary a quadratic, not exponential, speedup against symmetric-key brute-force search, which is why... | D |
| `gri2025timelinereport` | Expert-survey-based CRQC timeline estimates are updated periodically; the Global Risk Institute's most recent annual survey of quantum-co... | D |
| `groveroraclesaes2020` | Grover's algorithm gives a quantum adversary a quadratic, not exponential, speedup against symmetric-key brute-force search, which is why... | D |
| `hndltimemodel2025` | A more formal, explicitly time-dependent HNDL threat and migration model built on this same reasoning has since been proposed~, and an Io... | D |
| `hybridmedicalimage2024` | On the QKD-for-medical-data side: hybrid quantum-classical encryption has been proposed for medical image transmission in IoT-based telem... | D |
| `ietf2025rfc9771` | A formal quantum IND-CPA security treatment of AEAD constructions specifically~ and the IETF's own systematized statement of AEAD securit... | D |
| `ietf2026compositemlkem` | Alignment with formal composite-KEM standardization efforts currently under discussion in relevant standards bodies --- specifically an I... | D |
| `ietf2026kemcombiners` | Alignment with formal composite-KEM standardization efforts currently under discussion in relevant standards bodies --- specifically an I... | D |
| `ietf2026mlkemtls` | A deployed industry precedent for the flat-concatenation approach this paper ultimately uses exists in two IETF Internet-Drafts specifyin... | D |
| `ietf2026telecompqc` | Adaptive and staged migration to quantum-safe cryptography is an active concern beyond any single evaluated mechanism: NIST's own guidanc... | D |
| `ietf2026tlshybrid` | A deployed industry precedent for the flat-concatenation approach this paper ultimately uses exists in two IETF Internet-Drafts specifyin... | D |
| `ikev2constrained2024` | Beyond DNS, PQC overhead has been measured in IPsec directly~, in IKEv2 specifically under constrained and Internet-scale network conditi... | D |
| `iohtfog2025` | On resource-constrained medical devices specifically, lightweight post-quantum authentication has been proposed for medical Internet-of-T... | D |
| `ipsecpqcicisc2022` | Beyond DNS, PQC overhead has been measured in IPsec directly~, in IKEv2 specifically under constrained and Internet-scale network conditi... | D |
| `ipsecqkd5g2026` | Two further sources connect QKD/PQC specifically to mobile and 5G/6G-adjacent transport: a combined QKD-with-PQC design for sustainable m... | D |
| `kabanov2018practical` | Combining QKD with a computationally secure key rather than relying on QKD output alone is not itself a new idea in enterprise security p... | D |
| `kannwischer2019pqm4` | The pqm4 benchmarking framework for NIST PQC algorithms on ARM Cortex-M4 microcontrollers~, and its subsequent extension to additional po... | D |
| `kudaloor2026towardquantumsafe` | A further set of sources --- --- were located via live web search with real, specific titles, authors (where available), and venues ident... | D |
| `kyberphr2025` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `lightweightmedicaliot2023` | On resource-constrained medical devices specifically, lightweight post-quantum authentication has been proposed for medical Internet-of-T... | D |
| `lo2005decoystate` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `mahesh2025pcbqc` | A further set of sources --- --- were located via live web search with real, specific titles, authors (where available), and venues ident... | D |
| `maqsood2025enhancing` | A further set of sources --- --- were located via live web search with real, specific titles, authors (where available), and venues ident... | D |
| `mdi2025asymmetric` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `mdi2025freqcomb` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `mecsecuritysurvey2021` | Edge-specific security surveys, covering both the anticipated 6G network edge~ and the more mature, directly precedent 5G multi-access ed... | D |
| `mfaiomt2024` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `mlkemmldsaaes2025` | A formal quantum IND-CPA security treatment of AEAD constructions specifically~ and the IETF's own systematized statement of AEAD securit... | D |
| `mosca2018cybersecurity` | Mosca formalized the risk condition underlying this strategy as a simple inequality --- often called Mosca's theorem --- comparing the ti... | D |
| `moscarefinediot2022` | A more formal, explicitly time-dependent HNDL threat and migration model built on this same reasoning has since been proposed~, and an Io... | D |
| `nist2020sp80057` | More generally, the key-lifecycle stages this paper's Key-Management Component orchestrates --- generation, pooling, rotation, expiration... | D |
| `nist2023sp180038` | Independent, non-institutional analyses have engaged directly with the NSA's specific objections~ and have compared deployed QKD use case... | D |
| `nist2025cryptoagility` | Adaptive and staged migration to quantum-safe cryptography is an active concern beyond any single evaluated mechanism: NIST's own guidanc... | D |
| `nist2025pqcround4status` | Beyond the lattice family, NIST's fourth standardization round selected HQC, a code-based KEM built on the syndrome-decoding problem~, as... | D |
| `noninvasivepqcmedimage2026` | On the QKD-for-medical-data side: hybrid quantum-classical encryption has been proposed for medical image transmission in IoT-based telem... | D |
| `nsa2021qkdfaq` | National Security Agency's publicly stated skepticism toward QKD for national-security use, documented in the agency's own public FAQ on ... | D |
| `papadopoulos2026hybriddeployment` | A closely related mechanism has been evaluated for power-grid communications~, and hybrid QKD-PQC deployments for healthcare data exist i... | D |
| `pqc6gphysicallayer2024` | A physical-layer security scheme specifically combining 6G wireless transmission with PQC has also been proposed~, addressing a layer bel... | D |
| `pqcaie2024` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `pqcmigrationframework2023` | General frameworks for staged PQC migration with security-dependency analysis~ and strategic quantum-readiness architectures for risk man... | D |
| `pqcmobileresilience2026` | Beyond the wireless-security literature specifically, PQC integration into mobile-network resilience more broadly is an active area~, and... | D |
| `pqhealthcareroadmap2024` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `pqm4update2024` | The pqm4 benchmarking framework for NIST PQC algorithms on ARM Cortex-M4 microcontrollers~, and its subsequent extension to additional po... | D |
| `pqreadinessinternet2026` | At Internet scale, a large-scale measurement study of real-world PQC and hybrid TLS adoption across tens of thousands of domains provides... | D |
| `qkd2020trustednodefree` | Second, the achievable key-generation rate falls off with distance due to photon loss in the transmission medium, which bounds both the r... | D |
| `qkd2024satellite` | First, QKD requires dedicated physical infrastructure --- typically fiber-optic links, though free-space and satellite variants exist~ --... | D |
| `qkd2026metrofield` | Second, the achievable key-generation rate falls off with distance due to photon loss in the transmission medium, which bounds both the r... | D |
| `qkd2026multinode` | Second, the achievable key-generation rate falls off with distance due to photon loss in the transmission medium, which bounds both the r... | D |
| `qkdvspqccritical2025` | Independent, non-institutional analyses have engaged directly with the NSA's specific objections~ and have compared deployed QKD use case... | D |
| `quantumindcpaaead2025` | A formal quantum IND-CPA security treatment of AEAD constructions specifically~ and the IETF's own systematized statement of AEAD securit... | D |
| `quantumkeymedicalblockchain2025` | On the QKD-for-medical-data side: hybrid quantum-classical encryption has been proposed for medical image transmission in IoT-based telem... | D |
| `quantumkeystorage2024` | Adaptive buffering strategies aimed specifically at minimizing consumer-facing key-supply latency in QKD networks have also been proposed... | D |
| `quasar2025` | General frameworks for staged PQC migration with security-dependency analysis~ and strategic quantum-readiness architectures for risk man... | D |
| `quictlscomparative2025` | Sikeridis et al.\ provided one of the earliest systematic overhead assessments of PQC in TLS 1.3 and SSH~, and more recent work compares ... | D |
| `quiks2026adaptivebuffer` | Adaptive buffering strategies aimed specifically at minimizing consumer-facing key-supply latency in QKD networks have also been proposed... | D |
| `resourceconstrainedpqceval2025` | More recent surveys and comparative studies address the complexity and optimization strategies PQC requires specifically in embedded cont... | D |
| `risqv2020` | The pqm4 benchmarking framework for NIST PQC algorithms on ARM Cortex-M4 microcontrollers~, and its subsequent extension to additional po... | D |
| `roosan2025pqctelehealth` | A closely related mechanism has been evaluated for power-grid communications~, and hybrid QKD-PQC deployments for healthcare data exist i... | D |
| `scadacosim2025` | Closer to this paper's own domain analogy, adaptive and QKD-aware mechanisms have also been proposed for other critical-infrastructure se... | D |
| `scadasigncryption2022` | Closer to this paper's own domain analogy, adaptive and QKD-aware mechanisms have also been proposed for other critical-infrastructure se... | D |
| `secmedicalimage2021` | On the QKD-for-medical-data side: hybrid quantum-classical encryption has been proposed for medical image transmission in IoT-based telem... | D |
| `shor1997factoring` | Public-key cryptography deployed today --- RSA, elliptic-curve Diffie-Hellman, and their relatives --- derives its security from computat... | D |
| `sikeridis2020tlsoverhead` | Sikeridis et al.\ provided one of the earliest systematic overhead assessments of PQC in TLS 1.3 and SSH~, and more recent work compares ... | D |
| `simpy2024paper` | The system is implemented as a discrete-event simulation (using the SimPy library~) orchestrating simulated device/client transaction arr... | D |
| `sixgedgesecurity2023` | Edge-specific security surveys, covering both the anticipated 6G network edge~ and the more mature, directly precedent 5G multi-access ed... | D |
| `sixgsecprivacysurvey2021` | Broad requirements-and-security surveys of the anticipated 6G landscape~ and layer-by-layer treatments separating 6G's physical-connectio... | D |
| `sixgsecuritylayers2025` | Broad requirements-and-security surveys of the anticipated 6G landscape~ and layer-by-layer treatments separating 6G's physical-connectio... | D |
| `sixgsecuritysurveyjnca2024` | Broad requirements-and-security surveys of the anticipated 6G landscape~ and layer-by-layer treatments separating 6G's physical-connectio... | D |
| `southafricaehr2025` | On the PQC-for-healthcare side: ML-KEM has been applied specifically to personal health record encryption in cloud settings~; broader roa... | D |
| `spooren2026pqcenhanced` | A further set of sources --- --- were located via live web search with real, specific titles, authors (where available), and venues ident... | D |
| `stm32fpgacomparison2026` | More recent surveys and comparative studies address the complexity and optimization strategies PQC requires specifically in embedded cont... | D |
| `sustainablemobileqkdpqc2024` | Two further sources connect QKD/PQC specifically to mobile and 5G/6G-adjacent transport: a combined QKD-with-PQC design for sustainable m... | D |
| `terraquantum2023nsarebuttal` | Independent, non-institutional analyses have engaged directly with the NSA's specific objections~ and have compared deployed QKD use case... | D |
| `tfqkd2023nofreqdissem` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `tfqkd2024longdist` | The foundational protocol realizing this idea, BB84, was introduced by Bennett and Brassard in 1984~; subsequent protocol variants have t... | D |
| `threewayhybrid2025` | A cascade or nested combiner, $K = \mathrm{KDF}_2(\text{secret}_1, \mathrm{KDF}_1(\text{secret}_2))$, was considered as an alternative to... | D |
| `yamauchi2026tensorqml` | Yamauchi et al.\ propose a privacy-preserving federated learning framework combining tensor-network representation learning, multi-party-... | D |
| `zerotrust6gsurvey2024` | A physical-layer security scheme specifically combining 6G wireless transmission with PQC has also been proposed~, addressing a layer bel... | D |
| `zhu2025technoeconomic` | A closely related mechanism has been evaluated for power-grid communications~, and hybrid QKD-PQC deployments for healthcare data exist i... | D |