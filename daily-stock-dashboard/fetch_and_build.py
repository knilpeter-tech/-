# -*- coding: utf-8 -*-
import json, os, time, math, datetime
import pandas as pd
import yfinance as yf
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pytz

HERE = os.path.dirname(os.path.abspath(__file__))

def trailing_dividend_yield(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        last_close = float(hist["Close"].iloc[-1]) if len(hist) else float('nan')
        div = t.dividends
        trailing = float(div[-365:].sum()) if len(div) else 0.0
        if last_close and not math.isnan(last_close) and last_close != 0:
            return trailing / last_close
        return float('nan')
    except Exception:
        return float('nan')

def next_ex_div_date(ticker):
    # yfinance sometimes exposes exDividendDate via Ticker.get_info()
    try:
        t = yf.Ticker(ticker)
        cal = t.get_info()  # deprecated in future, but works in actions often
        val = cal.get("exDividendDate")
        if isinstance(val, (int, float)):
            # epoch seconds
            try:
                return datetime.datetime.utcfromtimestamp(val).date().isoformat()
            except Exception:
                return ""
        elif isinstance(val, str):
            return val
        return ""
    except Exception:
        return ""

def main():
    with open(os.path.join(HERE, "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)

    tz = pytz.timezone(cfg.get("timezone", "Asia/Seoul"))
    now = datetime.datetime.now(tz)

    rows = []
    for item in cfg["tickers"]:
        symbol = item["symbol"]
        name = item.get("name", "")
        try:
            t = yf.Ticker(symbol)
            info = t.fast_info if hasattr(t, "fast_info") else {}
            price = info.get("last_price")
            prev_close = info.get("previous_close") or info.get("last_price")

            if price is None:
                # fallback to history if fast_info unavailable
                hist = t.history(period="2d")
                if len(hist) >= 1:
                    price = float(hist["Close"].iloc[-1])
                if len(hist) >= 2:
                    prev_close = float(hist["Close"].iloc[-2])

            change = None
            changepct = None
            if price is not None and prev_close not in (None, 0):
                change = price - prev_close
                changepct = (change / prev_close) * 100.0

            ttm_yield = trailing_dividend_yield(symbol)
            exdiv = next_ex_div_date(symbol)

            rows.append({
                "symbol": symbol,
                "name": name,
                "price": price,
                "change": change,
                "changepct": changepct,
                "ttm_yield": ttm_yield,
                "ex_div_date": exdiv
            })
        except Exception as e:
            rows.append({
                "symbol": symbol,
                "name": name,
                "price": None,
                "change": None,
                "changepct": None,
                "ttm_yield": None,
                "ex_div_date": "",
                "error": str(e)
            })

    df = pd.DataFrame(rows)
    df.sort_values(by=["changepct"], ascending=False, inplace=True, na_position="last")

    # Render HTML
    env = Environment(
        loader=FileSystemLoader(os.path.join(HERE, "templates")),
        autoescape=select_autoescape()
    )
    tmpl = env.get_template("index.html.j2")
    html = tmpl.render(
        title=cfg.get("title", "주식 데일리 대시보드"),
        updated_at=now.strftime("%Y-%m-%d %H:%M %Z"),
        rows=df.to_dict(orient="records")
    )

    out_dir = os.path.join(HERE, "site")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Also write a CSV snapshot (useful for debugging)
    df.to_csv(os.path.join(out_dir, "data.csv"), index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
