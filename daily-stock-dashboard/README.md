# Daily Stock Dashboard (GitHub Pages + Python)

이 저장소는 `yfinance`로 한국/미국 주식 데이터를 수집해 **정적 HTML 대시보드**를 만들고,
**GitHub Actions**가 매일 자동으로 갱신하여 **GitHub Pages 링크**로 배포합니다.

## 빠른 시작
1) 이 폴더 전체를 새 GitHub 리포지토리로 업로드
2) 리포지토리 > Settings > Pages 에서 "Build and deployment: GitHub Actions" 선택
3) Actions 탭에서 `Build & Deploy Daily Stock Dashboard` 워크플로 실행(또는 하루 기다리면 매일 09:00 KST 자동 실행)
4) Pages URL(예: https://<아이디>.github.io/<리포지토리>) 이 **Daily Update 링크**가 됩니다.

## 티커 설정
- `config.json`의 `"tickers"` 배열에 종목을 추가/수정하세요.
- 한국 종목은 `.KS`(코스피) 또는 `.KQ`(코스닥) 접미사를 붙입니다. 예) 삼성전자: `005930.KS`

## 결과물
- `site/index.html` : 배포되는 대시보드
- `site/data.csv` : 같은 데이터의 CSV 스냅샷

## 주의
- 배당락일 등 세부 캘린더는 데이터 제공처(yfinance) 가용성에 따라 누락될 수 있습니다.
- 필요 시 증권사/거래소 API, FinanceDataReader 등으로 확장 가능합니다.
