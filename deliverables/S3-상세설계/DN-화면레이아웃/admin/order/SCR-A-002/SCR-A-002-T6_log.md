# 화면 레이아웃 — [SCR-A-002-T6] admin 주문 상세 · 변경이력 탭

> 상위 문서: [../SCR-A-002_detail.md](SCR-A-002_detail.md) · [../index.md](../index.md) · [../../index.md](../../index.md) · [../../../readme.md](../../../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, admin 채널) | **문서종류**: Design

---

## 11. admin — 주문 상세 · 변경이력 탭 (ChangeLogTab)

### 메타블록

| 항목 | 내용 |
|---|---|
| 화면 ID | SCR-A-002-T6 |
| 앱 | admin |
| 접근 권한 | [../SCR-A-002_detail.md](SCR-A-002_detail.md) 컨테이너(SCR-A-002)를 상속 — CS 담당자 (권한 체크 미적용 — 프로토타입) |
| 진입 조건 | [../SCR-A-002_detail.md](SCR-A-002_detail.md)(SCR-A-002) InnerTabs 활성 탭 = "변경이력" |
| 관련 세부UC | UC-14 ([DK-세부유스케이스/order.md](../../../../DK-세부유스케이스/order.md)) |
| 호출 API | [API-023](../../../../DL-인터페이스명세/order.md#api-023) (`GET /api/admin/v1/orders/{orderId}` → `history` 섹션, 2026-10-26 `logs`→`history` 전환) |

> **DQ 비고 갱신 대기 (2026-10-29)**: [DQ-프로그램목록/order.md](../../../../DQ-프로그램목록/order.md) SCR-A-002-T6 비고는 "`logs` 섹션"으로 적혀 있으나 DN·코드는 `history` 섹션이다(응답에 `logs`(Mock)도 남아 있어 혼동 소지). DQ 비고를 `history`로 고치는 작업은 DQ 별도 작업에서 진행한다.

> **구현 현황 (2026-10-29)**: 변경이력 탭은 `GET /api/admin/v1/orders/{orderId}`의 `history[]`(`ord_status_history` 영속 데이터)를 그린다. 결제하기 접수(TEMP → STOCK_REQUESTED) 이력은 `placeOrder()`가 기록하지만, 이후 STOCK_DEDUCTED·DEPOSIT_PENDING 전이와 결제상태(REQUESTED·WAITING_DEPOSIT) 이력은 재고차감 컨슈머와 Payment 도메인이 기록하는 설계(코드 주석 기준)라 현재 프로토타입에서는 STOCK_REQUESTED까지만 나타날 수 있다. 위 와이어프레임의 STOCK_* 단계는 비동기 접수 설계(2026-10-26) 기준이다.

### 와이어프레임

```
┌──────────────────────────────────────────────────────────────────────┐
│ [주문상품] [결제정보] [배송정보] [CS·클레임] [주문문의] [●변경이력]    │
├──────────────────────────────────────────────────────────────────────┤
│ 변경이력 탭                                                          │
│                                                                      │
│ ● 2026-10-26 11:20  결제상태: REQUESTED → WAITING_DEPOSIT          │
│ │  SYSTEM · PG 가상계좌 발급 수신, 입금 대기                         │
│ ○ 2026-10-26 11:20  주문상태: STOCK_DEDUCTED → DEPOSIT_PENDING      │
│ │  SYSTEM · 가상계좌 발급 완료                                       │
│ ○ 2026-10-26 11:20  결제상태: (신규) → REQUESTED                    │
│ │  SYSTEM · PG 결제 요청                                             │
│ ○ 2026-10-26 11:19  주문상태: STOCK_REQUESTED → STOCK_DEDUCTED      │
│ │  SYSTEM · 재고 차감 완료 (상품 API, SKU 단위)                      │
│ ○ 2026-10-26 11:19  주문상태: TEMP → STOCK_REQUESTED                │
│ │  CUSTOMER · 결제하기(주문 접수), 재고차감 요청 적재                │
│ ○ 2026-10-26 11:18  주문상태: (신규) → TEMP                         │
│ │  CUSTOMER · 주문서 진입, 임시주문 생성                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 화면 구성

| 영역 | 데이터 소스 (API) | 표시 내용 |
|---|---|---|
| 타임라인 | GET /api/admin/v1/orders/{orderId} → `history[]` | 일시, 대상(주문상태/결제상태/배송상태/클레임상태), 이전→이후 상태(최초 생성은 "(신규)"), 변경 주체 · 사유(`changedBy · reason`, 사유 없으면 주체만; 최신이 위 역순 정렬, 최신 1건은 강조 표시) |

### 화면 전환

> 해당 없음

### 유효성 검증

> 해당 없음 (조회 전용 탭)

### 상태별 UI

| 상태 | 화면 표현 |
|---|---|
| 이력 없음 | "변경 이력이 없습니다." |
| 로딩 중 | "불러오는 중..." 메시지 |

---

*공통 작성 규칙·채널별 패턴 요약·근거는 [../../../readme.md](../../../readme.md)에 있습니다.*
