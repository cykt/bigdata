# Week 6 관찰

## Task 1

Confidence는 대칭이 아니며, 이 데이터에서는 diaper→beer와 beer→diaper가 각각 0.8로 같지만 일반적으로 분모가 달라진다. lift가 1에 가까운 높은 confidence 규칙은 consequent가 원래 흔한 항목일 뿐일 수 있다.
item이 2,000개일 때 brute-force pair counter는 1,999,000개이며, 이 데이터에서 A-Priori는 pass 1 후 820,259개의 후보만 유지했다.

## Task 2

support 3까지 측정했지만 메모리 부족은 발생하지 않았으며, 측정 환경은 Windows 11, Python 3.13.9, Intel CPU이다.
support를 낮출 때 peak counter는 10,585→58,626→273,701→820,259개로 급증한 뒤 6 이하에서는 893,456개로 포화되었고, frequent pair는 249→776→2,244→6,397→17,045→43,116→101,938→250,054개로 계속 증가했다.

## Task 3

PCY bucket을 1,000,003개로 설정했으며, bucket 배열 자체도 메모리를 사용하므로 작은 데이터에서는 고정 비용 때문에 이득이 작다.
baseline의 peak counter 820,259개를 PCY는 23,356개로 줄여 97.2% 절감했고, frequent pair는 누락이나 추가 없이 완전히 동일했다.
