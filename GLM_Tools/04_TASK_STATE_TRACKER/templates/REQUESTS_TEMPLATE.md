# REQUESTS — istek günlüğü (x1..x5 akışının kaydı)

> Her kullanıcı mesajı bir `R-###`. Taskler isteklere bağlanır.
> "Hangi istekte ne kaldı?" sorusu her zaman buradan cevaplanır → amnezi denetlenebilir.

## Format

```
- R-### (YYYY-AA-GG SS:DD) mesajın tek cümlelik özeti → açılan/kapanan taskler
```

## Örnek akış (senin gerçek senaryonun çözülmüş hali)

```
- R-001 (2026-11-26 10:00) proje anlatıldı → T-001, T-002 açıldı
- R-002 (2026-11-26 11:30) "v2 update" → T-001 done (proofs/a0/...), T-003 açıldı
- R-003 (2026-11-26 13:00) 5'lik tasklist → T-004..T-008 AÇILDI (T-001..T-003 KORUNARAK)
- R-004 (2026-11-26 15:00) yeni tasklist istendi → T-009, T-010 eklendi;
  T-005..T-008 (x3'ten kalan 4 açık task) BİRLEŞTİRİLDİ, UNUTULMADI
```

## Kurallar (AI için)

1. Her kullanıcı mesajını işlemeden ÖNCE bu günlüğe bir R-### satırı düş.
2. Mesajdan çıkarılan her iş parçası `task_state.py add` ile tasks.json'a girer
   (nota `request_id: R-###` yazılır).
3. Oturum sonunda reconcile: her R'ye bağlı task durumu netleşir; açık kalanlar
   STATE.open_tasks listesinde taşınır.
