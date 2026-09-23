# ChatGPT Prompt and Response - Pairwise DOE Test Cases

## Prompt entered

> Create a pairwise (2-way) test suite for a mobile application. Return a complete tab-separated table with exactly these five columns: Type of Phone, Authentication, Connectivity, Memory, and Battery Level.
>
> Use only these levels:
>
> - Type of Phone: iPhone 14, iPhone 13, Galaxy Z, Huawei Mate, Google Pixel 7
> - Authentication: Fingerprint, Face recognition, Text Password
> - Connectivity: Wireless, 3G, 4G LTE, 5G Edge
> - Memory: 128 GB, 256 GB, 512 GB, 1 TB
> - Battery Level: <20%, 20-39%, 40-59%, 60-79%, 80-100%
>
> Every pair of values from every two different columns must occur in at least one row. Do not use values outside these lists. Do not include duplicate rows. After the table, state the number of test cases generated.

## ChatGPT response

The following pairwise suite contains 25 test cases.

```text
Type of Phone	Authentication	Connectivity	Memory	Battery Level
iPhone 14	Fingerprint	3G	1 TB	60-79%
Huawei Mate	Text Password	4G LTE	1 TB	20-39%
iPhone 13	Face recognition	4G LTE	256 GB	80-100%
Galaxy Z	Text Password	5G Edge	512 GB	<20%
Google Pixel 7	Fingerprint	Wireless	512 GB	80-100%
Google Pixel 7	Text Password	3G	256 GB	40-59%
Huawei Mate	Face recognition	5G Edge	128 GB	40-59%
iPhone 13	Text Password	Wireless	128 GB	60-79%
Galaxy Z	Face recognition	3G	128 GB	20-39%
iPhone 14	Face recognition	Wireless	256 GB	<20%
Google Pixel 7	Fingerprint	4G LTE	128 GB	<20%
iPhone 13	Fingerprint	5G Edge	256 GB	20-39%
Google Pixel 7	Face recognition	5G Edge	1 TB	60-79%
Galaxy Z	Fingerprint	Wireless	1 TB	40-59%
iPhone 14	Face recognition	4G LTE	512 GB	40-59%
iPhone 14	Text Password	5G Edge	128 GB	80-100%
Huawei Mate	Fingerprint	3G	512 GB	60-79%
iPhone 13	Text Password	3G	1 TB	<20%
Galaxy Z	Face recognition	4G LTE	256 GB	60-79%
Galaxy Z	Face recognition	3G	1 TB	80-100%
Huawei Mate	Text Password	Wireless	256 GB	<20%
iPhone 13	Fingerprint	5G Edge	512 GB	40-59%
Huawei Mate	Fingerprint	4G LTE	256 GB	80-100%
Google Pixel 7	Face recognition	Wireless	512 GB	20-39%
iPhone 14	Face recognition	Wireless	512 GB	20-39%
```

ChatGPT stated: `Number of test cases generated: 25`.

## Evidence and validation

- Screenshot: `screenshots/chatgptoutput.png`
- Exact table saved as: `chatgpt_pairwise_test_cases.tsv`
- Independent validation: 25 test cases, 0 duplicate rows, 0 invalid values, and 175/175 required value-pairs covered.
