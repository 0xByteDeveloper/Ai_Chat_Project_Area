# WORKLOG INDEX

| # | Dosya | Durum | Satır |
|---|---|---|---|
| 1 | WORKLOG_1.md | GÜNCEL | 0 |
| 2 | WORKLOG_2.md | arşiv | 200 |
| 3 | WORKLOG_3.md | GÜNCEL | 0 |

**Güncel worklog: WORKLOG_3.md**

> Rotasyon kuralı: güncel worklog 200 satıra ulaşınca
> `python GLM_Tools/03_WORKLOG_MANAGER/worklog_manager.py rotate`
> (arşiv + ÖZET + yeni worklog + bu index + STATE.json otomatik güncellenir).
>
> AI okuma kuralı: oturum başında yalnızca GÜNCEL worklogun son 40 satırı +
> (gerekirse) önceki ÖZETLER okunur; 500 satırlık arşivler yalnızca referans için vardır.
