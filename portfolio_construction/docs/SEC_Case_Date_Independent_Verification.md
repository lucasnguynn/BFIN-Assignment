# Member 2: SEC case-date evidence update (18 October 2026)

## Purpose and limits
This annex corroborates the **2015-2022-eligible universe**, namely 10 U.S. common stocks, VTV (large-cap value), IWM (U.S. small-cap) and the separate investable VTI comparator. It does **not** revise portfolio weights or consume 2023-2025 outcomes. The original case date is 31 December 2022; retrospective source access is documented separately.

**Important:** a source shown in a browser, an SEC filing index, a source URL, an SEC registration describing another fund, and original issuer document bytes are **different evidence levels**. The verified register records these distinctions. No source bytes from SEC were saved in this environment; do not claim `13/13 archived SEC originals`. All SEC SHA fields are deliberately blank.

## Strong contemporaneous ETF mandate evidence

- **VTV:** an SEC N-CEN filing dated **15 March 2022** explicitly lists Vanguard Value Index Fund ETF Shares (VTV). Separately, the fund's **26 April 2019 summary prospectus** describes large-capitalization value stocks and the CRSP US Large Cap Value Index. The SEC index is existence evidence; the 2019 *primary fund prospectus* supports the investment mandate. The 2019 document is older, not a claim that 2022 expense ratios equal those of 2019.
- **IWM:** an SEC iShares Trust filing dated **26 July 2022** lists iShares Russell 2000 ETF (IWM). A **26 September 2022 SEC registration by a separate issuer (First Trust Exchange-Traded Fund VIII)** quotes the IWM prospectus of **1 August 2022** and describes the Russell 2000 Index as U.S. small-cap equities. This is *contemporaneous secondary SEC-filed evidence*, not an archived original IWM prospectus; retain the limitation.
- **VTI comparator:** a **2021 SEC VTI summary prospectus** describes tracking the broad U.S. total stock market. VTI is the tradable benchmark; its return is not equivalent to the French market factor.

## Direct sources

VTV 2022 SEC N-CEN: https://www.sec.gov/Archives/edgar/data/36405/000175272422062560/0001752724-22-062560-index.html

VTV 2019 summary prospectus: https://www.sec.gov/Archives/edgar/data/36405/000093247119006971/sp_966042019blueline2.htm

IWM July 2022 SEC index: https://www.sec.gov/Archives/edgar/data/1100663/000119312522202133/0001193125-22-202133-index.html

IWM September 2022 contemporaneous third-party SEC registration (quotes 2022 IWM prospectus): https://www.sec.gov/Archives/edgar/data/1667919/000144554622006561/etf8_485a.htm

VTI 2021 summary prospectus: https://www.sec.gov/Archives/edgar/data/36405/000168386321002782/f8731d1.htm

Ten common stocks: each company's dated SEC filing URL in `evidence/SEC_CASE_DATE_WEB_VERIFICATION_20261018.csv`; some large 10-K/10-Q pages could only be verified through SEC filing index, and **JPM was not independently reverified** in this round.

## Limitations that matter for grading

1. **Eligibility is not an ex ante security-selection experiment**: the 2026 constructed universe can be affected by survivorship/selection bias, even when each included name existed in 2022.
2. **Original SEC bytes are not in this ZIP.** The internet-disabled compute environment could not resolve `www.sec.gov`. Existing `src/archive_sec_filings.py` is an optional compliant archiver for the group's network-enabled computer, requiring the group's actual User-Agent contact information. A successful SEC fetch must write bytes and a SHA; a failed fetch remains FAIL.
3. The course **raw-data preservation requirement** primarily pertains to Yahoo market responses and French factor data. The former are archived here; the latter remain the domain of Member 3 and must be archived when collected.
4. No document dated after 31 Dec 2022 was used to justify a case-date recommendation.

## Offline quality gate

From package root, run:

```
python src/verify_case_date_sources.py --root .
python src/rebuild.py --root .
python -m unittest discover -s tests -v
```

For the optional SEC original-byte retrieval (separate, network-enabled environment with authorized identification):

```
python src/archive_sec_filings.py --root . --user-agent 'YOUR ACTUAL RESEARCH CONTACT'
```

Do **not** put a made-up email or institution in User-Agent, and do not mark any original archived until its bytes can be independently inspected and hashed.

## Suggested memo language

"We checked SEC filings dated no later than 31 December 2022 to document that the candidate U.S. stocks and the VTV/IWM ETFs were eligible at the case date. VTV represents large-cap value exposure; IWM represents U.S. small-cap exposure. A contemporaneous iShares filing and an SEC-filed September 2022 third-party disclosure substantiate IWM's identity and mandate. The universe was chosen retrospectively, which limits claims of an unbiased ex ante security-selection process. Some SEC source pointers were verified online rather than preserved as original bytes."
