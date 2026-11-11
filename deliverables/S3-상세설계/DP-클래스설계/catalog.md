# 클래스 설계 — Catalog 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Catalog) | **문서종류**: Design
> 도메인 간 공용 계약(PublicApi)은 Order 쪽 호출 인터페이스가 [common.md](common.md)에 정의돼
> 있으며, 본 문서는 그 계약을 **구현하는 쪽**(internal 컨트롤러)을 포함한다.

---

## 1. Catalog 도메인 — 패키지 구조

```
com.runnshop.catalog/
├── product/
│   ├── controller/
│   │   ├── AdminProductController.kt     (직매입 등록·심사·목록·상세·노출우선순위)
│   │   ├── PartnerProductController.kt   (입점형 등록·수정·목록·상세·단종·복제·대량등록, 2026-11-09 소급 반영)
│   │   └── MobileProductController.kt    (목록·검색·상세·재입고알림신청·공유메타데이터, 2026-11-09 소급 반영)
│   ├── service/
│   │   ├── ProductService.kt             (등록·심사·수정·단종·복제·대량등록 — 쓰기 전체, 2026-11-09 소급 반영)
│   │   ├── ProductQueryService.kt        (목록·검색·상세 조회 — 읽기 전체, 노출로직 포함)
│   │   └── ProductOptionService.kt       (옵션그룹·옵션값 설정, SKU 자동생성)
│   ├── repository/
│   │   ├── ProductRepository.kt
│   │   ├── ProductImageRepository.kt
│   │   └── ProductOptionGroupRepository.kt
│   ├── domain/
│   │   ├── Product.kt
│   │   ├── ProductImage.kt
│   │   ├── ProductOptionGroup.kt
│   │   └── ProductOptionValue.kt
│   └── dto/
│       ├── RegisterDirectProductRequest.kt
│       ├── RegisterVendorProductRequest.kt
│       ├── RejectRequest.kt
│       ├── SetOptionsRequest.kt
│       ├── ExposureOverrideRequest.kt
│       ├── ProductListResponse.kt
│       ├── ProductDetailResponse.kt
│       ├── DuplicateResponse.kt          (2026-11-09 소급 반영)
│       ├── BulkUploadResponse.kt         (2026-11-09 소급 반영)
│       └── ShareMetadataResponse.kt      (2026-11-09 소급 반영)
├── wishlist/                             (2026-11-09 소급 반영)
│   ├── controller/
│   │   └── MobileWishlistController.kt   (찜 등록·해제·목록조회)
│   ├── service/
│   │   └── WishlistService.kt
│   ├── repository/
│   │   └── ProductWishlistRepository.kt
│   ├── domain/
│   │   └── ProductWishlist.kt
│   └── dto/
│       └── WishlistListResponse.kt
├── stock/
│   ├── controller/
│   │   └── PartnerSkuController.kt       (재고 수량 변경, SKU 통합조회)
│   ├── service/
│   │   ├── StockService.kt               (재고 변경·선점·복원·자동전환 대안A)
│   │   └── RestockSubscriptionService.kt (재입고 알림 신청)
│   ├── repository/
│   │   ├── SkuRepository.kt
│   │   ├── StockHistoryRepository.kt
│   │   └── RestockSubscriptionRepository.kt
│   ├── domain/
│   │   ├── Sku.kt
│   │   ├── StockHistory.kt
│   │   └── RestockSubscription.kt
│   └── dto/
│       ├── ChangeStockRequest.kt
│       └── StockChangeResponse.kt
├── price/
│   ├── service/
│   │   ├── PriceService.kt               (정가·공급가·BASE판매가 설정 — 쓰기 API)
│   │   └── PriceScheduleService.kt       (Promotion 행사가 스케줄 등록·취소 — 컨슈머·내부API)
│   ├── repository/
│   │   └── PriceScheduleRepository.kt
│   ├── domain/
│   │   └── ProductPriceSchedule.kt
│   └── dto/
│       ├── ChangePriceRequest.kt
│       └── PriceScheduleResponse.kt
├── category/
│   ├── controller/
│   │   ├── AdminCategoryController.kt    (표준·전시 카테고리, 브랜드 CRUD)
│   │   ├── AdminDisplayCategoryProductController.kt (전시카테고리 상품순서, 2026-11-09 신설)
│   │   └── MobileDisplayCategoryController.kt (카테고리 메뉴 트리 조회, 2026-11-09 신설)
│   ├── service/
│   │   ├── CategoryService.kt
│   │   └── DisplayCategoryProductOrderService.kt (2026-11-09 신설)
│   ├── repository/
│   │   ├── CategoryRepository.kt
│   │   ├── CategoryAttributeRepository.kt
│   │   ├── DisplayCategoryRepository.kt
│   │   ├── BrandRepository.kt
│   │   └── ProductDisplayCategoryRepository.kt (2026-11-09 신설)
│   ├── domain/
│   │   ├── Category.kt
│   │   ├── CategoryAttribute.kt
│   │   ├── DisplayCategory.kt
│   │   ├── Brand.kt
│   │   └── ProductDisplayCategory.kt (2026-11-09 신설)
│   └── dto/
│       ├── CreateCategoryRequest.kt
│       ├── CategoryListResponse.kt
│       ├── DisplayCategoryProductListResponse.kt (2026-11-09 신설)
│       └── ReorderProductsRequest.kt (2026-11-09 신설)
├── gnb/                                  (2026-11-09 신설)
│   ├── controller/
│   │   ├── AdminGnbMenuController.kt     (등록·수정·삭제·순서저장)
│   │   └── MobileGnbMenuController.kt    (홈 화면 노출 조회)
│   ├── service/
│   │   └── GnbMenuService.kt
│   ├── repository/
│   │   └── GnbMenuRepository.kt
│   ├── domain/
│   │   └── GnbMenu.kt
│   └── dto/
│       ├── CreateGnbMenuRequest.kt
│       ├── ReorderGnbMenuRequest.kt
│       └── GnbMenuListResponse.kt
├── ranking/                              (2026-11-09 신설)
│   ├── controller/
│   │   └── MobileRankingController.kt    (실시간/일간/주간 랭킹 조회)
│   ├── service/
│   │   └── ProductSalesRankingQueryService.kt
│   ├── listener/
│   │   └── ProductSalesRankingListener.kt (StockChanged 내부 재구독, 비동기 집계)
│   ├── repository/
│   │   └── ProductSalesHourlyRepository.kt
│   ├── domain/
│   │   └── ProductSalesHourly.kt
│   └── dto/
│       └── RankingResponse.kt
├── display/
│   ├── controller/
│   │   ├── AdminDisplayPageController.kt (생성·수정·게시·종료·홈지정·목록·단건)
│   │   ├── MobileHomeController.kt       (홈 화면 조회)
│   │   └── MobileDisplayPageController.kt (전시 페이지 공유 메타데이터, 2026-11-09 소급 반영 — 비홈 페이지 뷰 화면 자체는 미설계)
│   ├── service/
│   │   ├── DisplayPageService.kt         (전시 페이지 CRUD·상태전이·홈 지정)
│   │   ├── HomeQueryService.kt           (홈 화면 섹션별 콘텐츠 resolve)
│   │   └── EventBannerScheduleService.kt (Promotion 기획전 배너 동기화)
│   ├── repository/
│   │   ├── DisplayPageRepository.kt
│   │   ├── DisplaySectionRepository.kt
│   │   ├── DisplayTemplateRepository.kt
│   │   └── EventBannerScheduleRepository.kt
│   ├── domain/
│   │   ├── DisplayPage.kt
│   │   ├── DisplaySection.kt
│   │   ├── DisplayTemplate.kt
│   │   └── EventBannerSchedule.kt
│   └── dto/
│       ├── CreateDisplayPageRequest.kt
│       ├── UpdateDisplayPageRequest.kt
│       └── HomeResponse.kt
├── internal/
│   ├── InternalProductController.kt      (Order·Promotion 연동 — PublicApi 구현체)
│   └── InternalSkuController.kt
├── client/
│   └── RecommendationSaaSClient.kt       (interface — 외부 추천 SaaS 연동)
└── event/
    ├── CatalogEventPublisher.kt
    ├── StockEventListener.kt             (ORDER_CANCELLED·RETURN_EXCHANGE_CONFIRMED 수신)
    ├── PromotionPriceEventListener.kt    (PROMOTION_PRICE_SCHEDULED·SCHEDULE_CANCELLED 수신)
    ├── ExhibitionBannerEventListener.kt  (PROMOTION_EXHIBITION_BANNER_SYNCED·SYNC_CANCELLED 수신)
    └── MemberEventListener.kt            (MemberWithdrawn 수신, 2026-11-09 소급 반영)
```

---

## 2. Catalog 도메인 — 클래스 상세

### AdminProductController

```kotlin
@RestController
@RequestMapping("/api/admin/v1/products")
class AdminProductController(
    private val productService: ProductService,
    private val productQueryService: ProductQueryService,
    private val priceService: PriceService, // 2026-11-09 소급 반영
    private val productOptionService: ProductOptionService // 2026-11-09 소급 반영
) {
    @PostMapping
    fun registerDirect(
        @RequestHeader("X-Admin-Id") adminId: String,
        @RequestBody request: RegisterDirectProductRequest
    ): ApiResponse<ProductResponse>
    // isDirectSourced=true 고정, DRAFT→ON_SALE 즉시 전환 (REQ-CAT-001)

    @PostMapping("/{productId}/review-start")
    fun startReview(@PathVariable productId: String): ApiResponse<ProductResponse>

    @PostMapping("/{productId}/approve")
    fun approve(@PathVariable productId: String): ApiResponse<ProductResponse>

    @PostMapping("/{productId}/reject")
    fun reject(
        @PathVariable productId: String,
        @RequestBody request: RejectRequest
    ): ApiResponse<ProductResponse>

    @PatchMapping("/{productId}")
    fun updateBasicInfo(
        @PathVariable productId: String,
        @RequestBody request: UpdateProductRequest
    ): ApiResponse<Unit>
    // partner와 동일 스펙, 소유자 검증 없음(admin은 전 상품 수정 가능)

    @PostMapping("/{productId}/discontinue")
    fun discontinue(@PathVariable productId: String): ApiResponse<ProductResponse>

    @PatchMapping("/{productId}/price")
    fun changePrice(
        @RequestHeader("X-Admin-Id") adminId: String,
        @PathVariable productId: String,
        @RequestBody request: ChangePriceRequest
    ): ApiResponse<PriceResponse>
    // (2026-11-09 소급 반영, 미진항목 #2 해소) priceService.changePrice(adminId, productId,
    // request, requireOwnership=false) 호출 — 소유자 검증 생략, createdBy=adminId (DL §16)

    @PostMapping("/{productId}/images")
    fun addImage(
        @PathVariable productId: String,
        @RequestPart file: MultipartFile
    ): ApiResponse<ImageResponse>
    // (2026-11-09 소급 반영, 미진항목 #1 해소) 소유자 검증 없음(admin은 전 상품 이미지 등록
    // 가능). API-CAT-044, DL §9

    @PostMapping("/{productId}/options")
    fun setOptions(
        @PathVariable productId: String,
        @RequestBody request: SetOptionsRequest
    ): ApiResponse<OptionSetResponse>
    // (2026-11-09 소급 반영, 미진항목 #1 해소) productOptionService.setOptions(productId,
    // request) 호출, 소유자 검증 없음. API-CAT-045, DL §10

    @PostMapping("/{productId}/option-values/{optionValueId}/image")
    fun uploadOptionImage(
        @RequestHeader("X-Admin-Id") adminId: String,
        @PathVariable productId: String,
        @PathVariable optionValueId: String,
        @RequestPart file: MultipartFile
    ): ApiResponse<OptionImageResponse>
    // (2026-11-09 신설) productOptionService.uploadOptionImage(adminId, productId,
    // optionValueId, file, requireOwnership=false) 호출, 소유자 검증 없음. API-CAT-050, DL §45

    @PatchMapping("/{productId}/exposure-override")
    fun setExposureOverride(
        @PathVariable productId: String,
        @RequestBody request: ExposureOverrideRequest
    ): ApiResponse<Unit>

    @GetMapping
    fun getProducts(filter: AdminProductFilter): ApiResponse<ProductListResponse>
    // status=REVIEW_REQUESTED 필터링 시 심사 목록 화면(SCR-A-C02) 데이터 소스

    @GetMapping("/{productId}")
    fun getProductDetail(@PathVariable productId: String): ApiResponse<ProductDetailResponse>
    // rejectReason·rejectCount·isDirectSourced·exposureMdOverride 등 운영 전용 필드 포함
}
```

### PartnerProductController

```kotlin
@RestController
@RequestMapping("/api/partner/v1/products")
class PartnerProductController(
    private val productService: ProductService,
    private val productOptionService: ProductOptionService,
    private val priceService: PriceService,
    private val productQueryService: ProductQueryService
) {
    @PostMapping
    fun registerDraft(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @RequestBody request: RegisterVendorProductRequest
    ): ApiResponse<ProductResponse>
    // isDirectSourced=false 고정, DRAFT 생성 (REQ-CAT-002)

    @PostMapping("/{productId}/review-request")
    fun requestReview(@PathVariable productId: String): ApiResponse<ProductResponse>

    @PostMapping("/{productId}/resubmit")
    fun resubmit(@PathVariable productId: String): ApiResponse<ProductResponse>
    // REJECTED→DRAFT, 30일 초과 시 404 (배치가 이미 삭제)

    @PatchMapping("/{productId}")
    fun updateBasicInfo(
        @PathVariable productId: String,
        @RequestBody request: UpdateProductRequest
    ): ApiResponse<Unit>

    @PostMapping("/{productId}/images")
    fun addImage(
        @PathVariable productId: String,
        @RequestPart file: MultipartFile
    ): ApiResponse<ImageResponse>

    @PostMapping("/{productId}/options")
    fun setOptions(
        @PathVariable productId: String,
        @RequestBody request: SetOptionsRequest
    ): ApiResponse<OptionSetResponse>

    @PostMapping("/{productId}/option-values/{optionValueId}/image")
    fun uploadOptionImage(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @PathVariable productId: String,
        @PathVariable optionValueId: String,
        @RequestPart file: MultipartFile
    ): ApiResponse<OptionImageResponse>
    // (2026-11-09 신설) productOptionService.uploadOptionImage(vendorId, productId,
    // optionValueId, file, requireOwnership=true) 호출. API-CAT-049, DL §45

    @PostMapping("/{productId}/discontinue")
    fun discontinue(@PathVariable productId: String): ApiResponse<ProductResponse>

    @PatchMapping("/{productId}/price")
    fun changePrice(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @PathVariable productId: String,
        @RequestBody request: ChangePriceRequest
    ): ApiResponse<PriceResponse>
    // priceService.changePrice(vendorId, productId, request, requireOwnership=true) 호출

    @GetMapping("/{productId}/price-schedule")
    fun getPriceSchedule(@PathVariable productId: String): ApiResponse<PriceScheduleResponse>

    @GetMapping
    fun getMyProducts(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        filter: PartnerProductFilter
    ): ApiResponse<ProductListResponse>

    @GetMapping("/{productId}")
    fun getProductDetail(@PathVariable productId: String): ApiResponse<ProductDetailResponse>
    // 본인 소유 아니면 FORBIDDEN(403)

    @PostMapping("/{productId}/duplicate")
    fun duplicate(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @PathVariable productId: String
    ): ApiResponse<DuplicateResponse>
    // 본인 상품 아니면 FORBIDDEN(403) (2026-11-09 소급 반영, REQ-CAT-056)

    @PostMapping("/bulk-upload")
    fun bulkUpload(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @RequestPart file: MultipartFile
    ): ApiResponse<BulkUploadResponse>
    // 행 단위 부분 성공 허용 (2026-11-09 소급 반영, REQ-CAT-057)
}
```

### MobileProductController

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/products")
class MobileProductController(
    private val productQueryService: ProductQueryService,
    private val restockSubscriptionService: RestockSubscriptionService
) {
    @GetMapping
    fun getProducts(filter: MobileProductFilter): ApiResponse<ProductListResponse>
    // filter.displayCategoryId (2026-11-09 변경, 舊 categoryId). ON_SALE/SOLD_OUT만,
    // release_date 게이트·is_exposed=true 게이트(2026-11-09 신설, DBA §2.16)·정렬(카테고리
    // 지정 시 §2.5.3, 아니면 §2.6) 선반영 (REQ-CAT-029, 033~034, 037, 072, 082)

    @GetMapping("/search")
    fun searchProducts(query: SearchQuery): ApiResponse<ProductListResponse>
    // name·tags 매칭 + is_exposed=true AND is_search_excluded=false 게이트 (2026-11-09 신설,
    // REQ-CAT-083)

    @GetMapping("/{productId}")
    fun getProductDetail(
        @PathVariable productId: String,
        @RequestHeader("X-Member-Id", required = false) memberId: String?
    ): ApiResponse<ProductDetailResponse>
    // memberId 유무로 화면그룹(비로그인B/로그인B) 판별, discountExposure 필터링 (DBA §7.3).
    // is_exposed=false 또는 release_date 미도달이면 딥링크도 ProductNotFoundException(404)
    // (2026-11-09 신설, DBA §2.16)

    @PostMapping("/{productId}/restock-subscriptions")
    fun subscribeRestock(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable productId: String,
        @RequestBody request: RestockSubscribeRequest
    ): ApiResponse<SubscriptionResponse>

    @GetMapping("/{productId}/share")
    fun getShareMetadata(@PathVariable productId: String): ApiResponse<ShareMetadataResponse>
    // 인증 불필요, 기존 데이터 재사용(2026-11-09 소급 반영, REQ-CAT-063)
}
```

### ProductService

```kotlin
@Service
@Transactional
class ProductService(
    private val productRepository: ProductRepository,
    private val productImageRepository: ProductImageRepository,
    private val eventPublisher: CatalogEventPublisher,
    private val wishlistService: WishlistService // 2026-11-09 소급 반영
) {
    fun registerDirectSourced(adminId: String, request: RegisterDirectProductRequest): ProductResponse
    // isDirectSourced=true, 가격구조 검증 후 상태 DRAFT→ON_SALE 즉시 전환, ProductDirectListed 발행

    fun registerDraft(vendorId: String, request: RegisterVendorProductRequest): ProductResponse
    // isDirectSourced=false, DRAFT 생성

    fun requestReview(vendorId: String, productId: String): ProductResponse
    // 소유자·상태(DRAFT)·이미지(≥1장) 검증 후 REVIEW_REQUESTED, ProductCreated 발행

    fun startReview(productId: String): ProductResponse
    // REVIEW_REQUESTED→UNDER_REVIEW

    fun decideReview(adminId: String, productId: String, decision: ReviewDecision): ProductResponse
    // APPROVE: UNDER_REVIEW→ON_SALE, ProductApproved 발행
    // REJECT: UNDER_REVIEW→REJECTED, rejectCount+1·rejectedAt 갱신, 3회 이상 시 에스컬레이션 표시, ProductRejected 발행

    fun resubmit(vendorId: String, productId: String): ProductResponse
    // REJECTED→DRAFT, 30일 초과 시 ProductNotFoundException(배치가 이미 삭제)

    fun updateBasicInfo(productId: String, request: UpdateProductRequest)
    // name·categoryId·releaseDate·description·maxOrderQuantity·summary·tags·isExposed·
    // isSearchExcluded 등 부분 수정(maxOrderQuantity는 2026-11-09 소급 반영, nullable=무제한,
    // 1 이상 정수만 허용; summary 200자/tags 10개 제한은 400/422 검증; isExposed·
    // isSearchExcluded는 2026-11-09 신설, DBA §2.16 — 상태 전이 없이 단순 플래그 갱신), price
    // 필드는 PriceService 전용,
    // ProductUpdated 발행

    fun discontinue(productId: String): ProductResponse
    // ON_SALE/SOLD_OUT→DISCONTINUED, 재고 수량과 무관한 수동 전환만 허용
    // wishlistService.deleteAllByProduct(productId) 호출(2026-11-09 소급 반영, REQ-CAT-062)

    fun setExposureOverride(productId: String, override: Int?)
    // null이면 해제(AI점수/default_order로 복귀)

    fun expireOverdueRejectedProducts(): Int
    // [배치, 60분 주기] REJECTED 상태 && now-rejectedAt>30일 && 미재제출 상품 자동 삭제

    fun duplicate(vendorId: String, productId: String): DuplicateResponse
    // (2026-11-09 소급 반영) 본인 소유 아니면 ForbiddenException(403). 가격·재고·판매자상품코드
    // 제외 전체 필드 복사 + 신규 productId/skuId 발급, 이미지는 원본 image_url 그대로 참조
    // (재업로드 없음), 옵션그룹·옵션값도 동일 구조로 복사해 SKU 재생성. 상태 DRAFT (REQ-CAT-056)

    fun bulkCreate(vendorId: String, rows: List<BulkProductRow>): BulkUploadResponse
    // (2026-11-09 소급 반영) 행 단위 독립 트랜잭션. 필수 필드·가격구조 검증 실패 행은 결과의
    // failures[]에 사유와 함께 기록하고, 나머지 성공 행은 DRAFT로 생성(부분 성공 허용, REQ-CAT-057)
}
```

### ProductQueryService

```kotlin
@Service
@Transactional(readOnly = true)
class ProductQueryService(
    private val productRepository: ProductRepository,
    private val productDisplayCategoryRepository: ProductDisplayCategoryRepository, // 2026-11-09 신설
    private val recommendationSaaSClient: RecommendationSaaSClient
) {
    fun getProducts(filter: AdminProductFilter): ProductListResponse
    fun getMyProducts(vendorId: String, filter: PartnerProductFilter): ProductListResponse
    fun getProductDetail(productId: String): ProductDetailResponse
    // admin/partner 공용 — rejectReason 등 운영 필드 포함, partner 호출 시 소유자 검증

    fun getMobileProducts(filter: MobileProductFilter): ProductListResponse
    // filter.displayCategoryId 있으면 cat_product_display_category JOIN,
    //   ORDER BY isPinned DESC, sortOrder ASC (DBA §2.5.3, 2026-11-09 변경)
    // 없으면 WHERE status IN (ON_SALE,SOLD_OUT) AND (releaseDate IS NULL OR releaseDate<=now)
    //   ORDER BY COALESCE(exposureMdOverride, exposureAiScore, defaultOrder) (기존 기본값)
    // price는 PriceScheduleRepository JOIN으로 조회시점 유효 판매가 resolve (DBA §4.1-1)

    fun searchProducts(query: SearchQuery): ProductListResponse

    fun getMobileProductDetail(productId: String, memberId: String?): ProductDetailResponse
    // discountExposure 필터링(DBA §7.3) + recommendationSaaSClient.getRecommendations() 호출
    // SaaS 실패 시 빈 배열 반환(Human Review, DBA §7.4)

    fun getShareMetadata(productId: String): ShareMetadataResponse
    // (2026-11-09 소급 반영) name·thumbnailUrl·description 재사용, 신규 필드 없음 (REQ-CAT-063)

    fun getMaxOrderQuantity(productId: String): Int?
    // (2026-11-09 소급 반영) Promotion 연동 전용. null=무제한 (REQ-CAT-059b)
}
```

### ProductOptionService

```kotlin
@Service
@Transactional
class ProductOptionService(
    private val optionGroupRepository: ProductOptionGroupRepository,
    private val optionValueRepository: ProductOptionValueRepository, // 2026-11-09 신설
    private val skuRepository: SkuRepository
) {
    fun setOptions(vendorId: String, productId: String, request: SetOptionsRequest): OptionSetResponse
    // depth>2면 OptionDepthExceededException
    // 옵션값 조합(cartesian product)으로 SKU 자동 생성

    fun uploadOptionImage(actorId: String, productId: String, optionValueId: String, file: MultipartFile, requireOwnership: Boolean = true): OptionImageResponse
    // (2026-11-09 신설) actorId는 vendorId(partner 경로, requireOwnership=true) 또는 adminId
    // (admin 경로, requireOwnership=false)를 받는다(priceService.changePrice와 동일 패턴).
    // optionValue 소속 옵션그룹 depth!=1이면 OptionImageDepthInvalidException(422,
    // OPTION_IMAGE_DEPTH_INVALID). requireOwnership=true인데 본인 상품이 아니면
    // ForbiddenException. 업로드 성공 시 cat_product_option_value.image_url 갱신(덮어쓰기)
}
```

### MobileWishlistController / WishlistService (2026-11-09 소급 반영)

```kotlin
@RestController
@RequestMapping("/api/mobile/v1")
class MobileWishlistController(
    private val wishlistService: WishlistService
) {
    @PostMapping("/products/{productId}/wishlist")
    fun add(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable productId: String
    ): ApiResponse<WishlistActionResponse>

    @DeleteMapping("/products/{productId}/wishlist")
    fun remove(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable productId: String
    ): ApiResponse<WishlistActionResponse>

    @GetMapping("/me/wishlist")
    fun getMyWishlist(
        @RequestHeader("X-Member-Id") memberId: String,
        @RequestParam(defaultValue = "1") page: Int,
        @RequestParam(defaultValue = "20") size: Int
    ): ApiResponse<WishlistListResponse>
}

@Service
@Transactional
class WishlistService(
    private val productWishlistRepository: ProductWishlistRepository
) {
    fun add(memberId: String, productId: String): WishlistActionResponse
    // (product_id, member_id) unique — 이미 존재하면 그대로 isWished=true 반환(멱등)

    fun remove(memberId: String, productId: String)
    // deleteByProductIdAndMemberId, 없어도 에러 없이 무시(멱등)

    fun getMyWishlist(memberId: String, page: Int, size: Int): WishlistListResponse
    // findByMemberIdOrderByCreatedAtDesc — SOLD_OUT/DISCONTINUED 전환 시 이미 행이 삭제돼 있어
    // 별도 상태 필터 불필요(REQ-CAT-061~062)

    fun deleteAllByProduct(productId: String)
    // ProductService.discontinue()/StockService 자동전환 로직에서 호출되는 내부 부수효과
    // (SOLD_OUT/DISCONTINUED 전환 시 전체 삭제, 별도 이벤트 없음, DBA §1.14)

    fun deleteAllByMember(memberId: String)
    // (2026-11-09 소급 반영) MemberEventListener가 MemberWithdrawn 수신 시 호출
    // (DBA §1.14 "Member와의 경계", REQ-CAT-062, PGM: CSM-CAT-008)
}
```

### StockService

```kotlin
@Service
@Transactional
class StockService(
    private val skuRepository: SkuRepository,
    private val productRepository: ProductRepository,
    private val stockHistoryRepository: StockHistoryRepository,
    private val restockSubscriptionRepository: RestockSubscriptionRepository,
    private val eventPublisher: CatalogEventPublisher,
    private val wishlistService: WishlistService // 2026-11-09 소급 반영
) {
    fun changeStock(vendorId: String, skuId: String, request: ChangeStockRequest): StockChangeResponse
    // 판매자 직접 등록(changeType=RESTOCK_VENDOR). 자동전환(대안A) 아래 공통 로직 재사용

    fun reserve(skuId: String, quantity: Int, orderId: String): StockChangeResponse
    // 동기 PublicApi(Order). availableQuantity 부족 시 InsufficientStockException(409)
    // 0 되면 상태 ON_SALE→SOLD_OUT

    fun restore(skuId: String, quantity: Int, changeType: StockChangeType)
    // 비동기(ORDER_CANCELLED/RETURN_EXCHANGE_CONFIRMED 수신). 자동전환(대안A) 공통 로직 재사용

    private fun applyAutoTransition(sku: Sku, product: Product)
    // [대안A 핵심] 발생원인 무관, product.status==SOLD_OUT && sku.availableQuantity>0이면
    // MD 확인 없이 SOLD_OUT→ON_SALE 전환 + restockSubscriptionRepository의 PENDING 건을
    // NOTIFIED로 전환·발송. changeStock/reserve/restore 3개 메서드가 공통으로 호출
    // reserve()로 availableQuantity가 0이 되어 product.status가 SOLD_OUT으로 바뀌는 경로에서도
    // wishlistService.deleteAllByProduct(productId)가 함께 호출된다(2026-11-09 소급 반영, REQ-CAT-062)
}

enum class StockChangeType { RESERVE, RESTORE_ORDER_CANCEL, RESTORE_RETURN_EXCHANGE, RESTOCK_VENDOR, MANUAL_ADJUST }
```

### RestockSubscriptionService

```kotlin
@Service
@Transactional
class RestockSubscriptionService(
    private val restockSubscriptionRepository: RestockSubscriptionRepository
) {
    fun subscribe(memberId: String, skuId: String): SubscriptionResponse
    // SKU가 SOLD_OUT 아니면 SkuNotSoldOutException(409)
}
```

### PriceService

```kotlin
@Service
@Transactional
class PriceService(
    private val productRepository: ProductRepository,
    private val priceScheduleRepository: PriceScheduleRepository
) {
    fun changePrice(actorId: String, productId: String, request: ChangePriceRequest, requireOwnership: Boolean = true): PriceResponse
    // (2026-11-09 소급 반영) actorId는 vendorId(partner 경로, requireOwnership=true) 또는
    // adminId(admin 경로, requireOwnership=false)를 받는다. requireOwnership=true인데 본인
    // 상품이 아니면 ForbiddenException(403). priceOriginal >= priceSale >= priceSupply 위반 시
    // PriceRuleViolationException(422). priceOriginal·priceSupply는 cat_product에 즉시 반영.
    // priceSale은 기존 BASE 스케줄 행 end_at=now 종료 후 신규 BASE(start_at=now, end_at=null,
    // createdBy=actorId) 행 추가 (DBA §4.1-1, "마스터 속성과 변동 속성 분리")

    fun getPriceSchedule(productId: String): PriceScheduleResponse
    // 과거·현재·예약 전체 이력 조회 (이력+예약 겸용 테이블을 그대로 노출)
}
```

### PriceScheduleService

```kotlin
@Service
@Transactional
class PriceScheduleService(
    private val priceScheduleRepository: PriceScheduleRepository
) {
    fun registerSchedule(productId: String, sourceEventId: String, price: Int, startAt: Instant, endAt: Instant?)
    // Promotion 행사가 반영. source_type=PROMOTION_EVENT 행 추가. 사전 등록 가능(startAt 미래 허용)
    // 기간 중복 체크 없이 그대로 추가 (Human Review — Promotion 정책 소관, DBA §4.1-1)

    fun cancelSchedule(productId: String, sourceEventId: String)
    // 행사 중도 취소. endAt=now로 종료 처리(물리 삭제 아님). 정상 종료는 이 메서드 호출 없이
    // endAt 경과로 조회 시점에 자동 처리됨
}
```

### CategoryService

```kotlin
@Service
@Transactional
class CategoryService(
    private val categoryRepository: CategoryRepository,
    private val displayCategoryRepository: DisplayCategoryRepository,
    private val brandRepository: BrandRepository
) {
    fun createCategory(request: CreateCategoryRequest): CategoryResponse
    // 중복 이름 시 DuplicateCategoryNameException(409). 단일계층(대분류만)

    fun updateCategory(categoryId: String, request: UpdateCategoryRequest)
    fun deleteCategory(categoryId: String)  // is_active=false
    fun getCategories(): CategoryListResponse

    fun createDisplayCategory(request: CreateDisplayCategoryRequest): DisplayCategoryResponse
    fun getDisplayCategories(): DisplayCategoryListResponse  // 트리 구조 반환, pagination 없음

    fun createBrand(request: CreateBrandRequest): BrandResponse
    fun getBrands(): BrandListResponse

    fun getActiveDisplayCategoryTree(): DisplayCategoryListResponse  // 2026-11-09 신설
    // is_active=true만 반환. MobileDisplayCategoryController에서 사용(admin용 getDisplayCategories와 분리)
}
```

### MobileDisplayCategoryController (2026-11-09 신설)

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/display-categories")
class MobileDisplayCategoryController(
    private val categoryService: CategoryService
) {
    @GetMapping
    fun getDisplayCategories(): ApiResponse<DisplayCategoryListResponse>
    // categoryService.getActiveDisplayCategoryTree() — 인증 불필요
}
```

### AdminDisplayCategoryProductController / DisplayCategoryProductOrderService (2026-11-09 신설)

```kotlin
@RestController
@RequestMapping("/api/admin/v1/display-categories/{displayCategoryId}/products")
class AdminDisplayCategoryProductController(
    private val orderService: DisplayCategoryProductOrderService
) {
    @GetMapping
    fun getProducts(@PathVariable displayCategoryId: String): ApiResponse<DisplayCategoryProductListResponse>
    // is_pinned DESC, sort_order ASC 반환. 페이지네이션 없음(DN-admin §8)

    @PutMapping("/order")
    fun reorder(
        @PathVariable displayCategoryId: String,
        @RequestBody request: ReorderProductsRequest
    ): ApiResponse<Unit>
    // 요청 배열 순서를 그대로 sortOrder(0..n-1)로 전체 교체, isPinned 함께 저장
}

@Service
@Transactional
class DisplayCategoryProductOrderService(
    private val productDisplayCategoryRepository: ProductDisplayCategoryRepository,
    private val displayCategoryRepository: DisplayCategoryRepository
) {
    fun getProducts(displayCategoryId: String): DisplayCategoryProductListResponse
    // displayCategoryRepository.findById 없으면 DisplayCategoryNotFoundException(404)
    // productDisplayCategoryRepository.findByDisplayCategoryIdOrderByIsPinnedDescSortOrderAsc(displayCategoryId)

    fun reorder(displayCategoryId: String, request: ReorderProductsRequest) {
        // 1. request.products의 모든 productId가 해당 displayCategoryId에 매핑돼 있는지 검증
        //    하나라도 없으면 ProductNotMappedException(400)
        // 2. index 순서대로 sortOrder=0,1,2... 부여, isPinned 갱신 후 일괄 save (전체 교체)
    }
}
```

### AdminGnbMenuController / MobileGnbMenuController / GnbMenuService (2026-11-09 신설)

```kotlin
@RestController
@RequestMapping("/api/admin/v1/gnb-menus")
class AdminGnbMenuController(
    private val gnbMenuService: GnbMenuService
) {
    @PostMapping
    fun create(
        @RequestHeader("X-Admin-Id") adminId: String,
        @RequestBody request: CreateGnbMenuRequest
    ): ApiResponse<GnbMenuResponse>
    // linkType=DISPLAY_PAGE/DISPLAY_CATEGORY면 존재 검증, 그 외는 검증 없음

    @PatchMapping("/{menuId}")
    fun update(
        @PathVariable menuId: String,
        @RequestBody request: CreateGnbMenuRequest
    ): ApiResponse<GnbMenuResponse>

    @DeleteMapping("/{menuId}")
    fun delete(@PathVariable menuId: String): ApiResponse<Unit>

    @PatchMapping("/order")
    fun reorder(@RequestBody request: ReorderGnbMenuRequest): ApiResponse<Unit>
    // 요청 배열 순서를 그대로 sortOrder(0..n-1)로 전체 교체(§24 전시카테고리 상품순서와 동일)

    @GetMapping
    fun getAll(): ApiResponse<GnbMenuListResponse>
    // is_exposed·전시기간 무관 전체 목록(관리 화면용, 페이지네이션 없음)
}

@RestController
@RequestMapping("/api/mobile/v1/gnb-menus")
class MobileGnbMenuController(
    private val gnbMenuService: GnbMenuService
) {
    @GetMapping
    fun getExposedMenus(): ApiResponse<GnbMenuListResponse>
    // 인증 불필요. is_exposed=true AND 전시기간 이내인 메뉴만 sortOrder ASC
}

@Service
@Transactional
class GnbMenuService(
    private val gnbMenuRepository: GnbMenuRepository,
    private val displayPageRepository: DisplayPageRepository,
    private val displayCategoryRepository: DisplayCategoryRepository
) {
    fun create(adminId: String, request: CreateGnbMenuRequest): GnbMenuResponse
    // linkType==DISPLAY_PAGE: displayPageRepository.findBySlug 없으면 DisplayPageNotFoundException(404)
    // linkType==DISPLAY_CATEGORY: displayCategoryRepository.findById 없으면 DisplayCategoryNotFoundException(404)
    // linkType==EVENT_PAGE/EXTERNAL_URL/RANKING: 검증 없이 linkTarget 그대로 저장
    // createdBy=adminId, sortOrder=현재 최대값+1

    fun update(menuId: String, request: CreateGnbMenuRequest): GnbMenuResponse
    fun delete(menuId: String)

    fun reorder(request: ReorderGnbMenuRequest)
    // 요청 menuIds 순서대로 sortOrder=0,1,2... 일괄 저장(전체 교체)

    fun getAll(): GnbMenuListResponse
    // is_exposed·전시기간 무관, sortOrder ASC 전체 반환

    @Transactional(readOnly = true)
    fun getExposedMenus(): GnbMenuListResponse
    // gnbMenuRepository.findExposedOrderBySortOrder(now) — is_exposed=true AND
    // (displayStartAt IS NULL OR displayStartAt<=now) AND (displayEndAt IS NULL OR displayEndAt>now)
}

enum class GnbLinkType { DISPLAY_PAGE, DISPLAY_CATEGORY, RANKING, EVENT_PAGE, EXTERNAL_URL }
```

### MobileRankingController / ProductSalesRankingQueryService (2026-11-09 신설)

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/products")
class MobileRankingController(
    private val rankingQueryService: ProductSalesRankingQueryService
) {
    @GetMapping("/ranking")
    fun getRanking(
        @RequestParam period: RankingPeriod,
        @RequestParam(required = false) displayCategoryId: String?
    ): ApiResponse<RankingResponse>
    // period: REALTIME(최근 3시간)/DAILY(오늘 00:00~)/WEEKLY(최근 7일). 인증 불필요
}

enum class RankingPeriod { REALTIME, DAILY, WEEKLY }

@Service
@Transactional(readOnly = true)
class ProductSalesRankingQueryService(
    private val productSalesHourlyRepository: ProductSalesHourlyRepository,
    private val productDisplayCategoryRepository: ProductDisplayCategoryRepository,
    private val productRepository: ProductRepository
) {
    fun getRanking(period: RankingPeriod, displayCategoryId: String?): RankingResponse
    // 1. period → [fromHour, now] 범위 산출
    // 2. displayCategoryId 있으면 productDisplayCategoryRepository로 대상 productId 집합 축소
    // 3. productSalesHourlyRepository.sumQuantityByHourRange(fromHour, now, productIds?)
    //    → GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 50
    // 4. ON_SALE/SOLD_OUT 외 상태 상품은 결과에서 제외 (DBA §2.13)
}
```

### ProductSalesRankingListener (2026-11-09 신설)

```kotlin
@Component
class ProductSalesRankingListener(
    private val processedEventRepository: ProcessedEventRepository,
    private val productSalesHourlyRepository: ProductSalesHourlyRepository
) {
    @EventListener
    fun onStockChanged(event: StockChangedEvent)
    // StockChanged를 Catalog가 자신의 이벤트로 "내부 재구독"한다(DI-이벤트플로우 §도메인
    // 내부 이벤트 참조). eventId로 멱등 검증(processedEventRepository) 후:
    // changeType in [RESERVE, RESTORE_ORDER_CANCEL] → sale_hour=truncate(now, HOUR) 기준
    //   productSalesHourlyRepository.upsert(productId, saleHour, event.changeQuantity) 원자적 증분
    // changeType in [RESTORE_RETURN_EXCHANGE, RESTOCK_VENDOR] → 무시(집계 제외, DBA §1.17)
    // StockService의 reserve()/restore() 트랜잭션과는 분리된 별도 트랜잭션 — 이 리스너가
    // 실패해도 재고·주문 처리에는 영향 없음
}
```

### AdminDisplayPageController

```kotlin
@RestController
@RequestMapping("/api/admin/v1/display-pages")
class AdminDisplayPageController(
    private val displayPageService: DisplayPageService
) {
    @PostMapping
    fun create(@RequestBody request: CreateDisplayPageRequest): ApiResponse<DisplayPageResponse>

    @PostMapping("/{pageId}/publish")
    fun publish(@PathVariable pageId: String): ApiResponse<DisplayPageResponse>

    @PatchMapping("/{pageId}")
    fun update(
        @PathVariable pageId: String,
        @RequestBody request: UpdateDisplayPageRequest  // title/slug/sections/displayStartAt/displayEndAt
    ): ApiResponse<DisplayPageResponse>
    // 상태 전이 없음. DRAFT·PUBLISHED 공통. displayEndAt 설정 시 displayStartAt 이후인지 검증
    // (2026-11-09: DRAFT_EDIT/SCHEDULED 제거로 edit-start/republish/schedule을 이 API로 통합)

    @PostMapping("/{pageId}/close")
    fun close(@PathVariable pageId: String): ApiResponse<DisplayPageResponse>

    @PatchMapping("/{pageId}/set-home")
    fun setHome(@PathVariable pageId: String): ApiResponse<DisplayPageResponse>
    // PUBLISHED 상태만 가능, 기존 홈 자동 해제 (REQ-CAT-052, 2026-10-26 신설)

    @GetMapping
    fun getPages(filter: DisplayPageFilter): ApiResponse<DisplayPageListResponse>

    @GetMapping("/{pageId}")
    fun getPageDetail(@PathVariable pageId: String): ApiResponse<DisplayPageDetailResponse>
    // sections[] 포함
}
```

### MobileHomeController

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/home")
class MobileHomeController(
    private val homeQueryService: HomeQueryService
) {
    @GetMapping
    fun getHome(): ApiResponse<HomeResponse>
    // is_home=true && status=PUBLISHED 페이지 없으면 HomeNotConfiguredException(404)
}
```

### MobileDisplayPageController (2026-11-09 소급 반영)

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/display-pages")
class MobileDisplayPageController(
    private val displayPageService: DisplayPageService,
    private val homeQueryService: HomeQueryService // 2026-11-09 신설
) {
    @GetMapping("/{pageId}/share")
    fun getShareMetadata(@PathVariable pageId: String): ApiResponse<ShareMetadataResponse>
    // 인증 불필요, 리워드 없음(REQ-CAT-063). 2026-11-09: 아래 getDisplayPage 신설로
    // 이 컨트롤러가 노출될 고객 화면(SCR-M-C07)이 생겨 미진항목 #9 해소

    @GetMapping("/{slug}")
    fun getDisplayPage(@PathVariable slug: String): ApiResponse<DisplayPageViewResponse>
    // (2026-11-09 신설, 미진항목 #9·#13 해소) homeQueryService.getDisplayPage(slug) 호출
    // — getHome()과 섹션 resolve 로직을 공유. 인증 불필요
    // status!=PUBLISHED 또는 is_exposed=false면 DisplayPageNotFoundException(404)
}
```

### DisplayPageService

```kotlin
@Service
@Transactional
class DisplayPageService(
    private val displayPageRepository: DisplayPageRepository,
    private val displaySectionRepository: DisplaySectionRepository
) {
    fun create(adminId: String, request: CreateDisplayPageRequest): DisplayPageResponse  // DRAFT
    fun publish(pageId: String): DisplayPageResponse        // DRAFT→PUBLISHED, publishedAt 기록
    fun update(pageId: String, request: UpdateDisplayPageRequest): DisplayPageResponse
    // title/sections/displayStartAt/displayEndAt 수정, 상태 전이 없음(DRAFT·PUBLISHED 공통)
    // displayEndAt 설정 시 displayStartAt 이후인지 검증 → 아니면 InvalidDisplayPeriodException(400)
    fun close(pageId: String): DisplayPageResponse           // PUBLISHED→CLOSED, closedAt 기록

    fun setHome(adminId: String, pageId: String): DisplayPageResponse
    // page.status!=PUBLISHED면 InvalidStatusException(409)
    // 기존 is_home=true 페이지 조회 후 false로 해제, 대상 페이지 is_home=true 설정 (REQ-CAT-052)

    fun publishDuePages(): Int
    // [배치, 1분 주기] status=DRAFT && displayStartAt<=now → PUBLISHED, publishedAt 기록
    fun closeDuePages(): Int
    // [배치, 1분 주기] status=PUBLISHED && displayEndAt<=now → CLOSED, closedAt 기록, isHome=false

    fun getPages(filter: DisplayPageFilter): DisplayPageListResponse
    fun getPageDetail(pageId: String): DisplayPageDetailResponse

    fun getShareMetadata(pageId: String): ShareMetadataResponse
    // (2026-11-09 소급 반영) title·slug 기반 shareUrl 재사용, 신규 필드 없음 (REQ-CAT-063)
}
```

### HomeQueryService

```kotlin
@Service
@Transactional(readOnly = true)
class HomeQueryService(
    private val displayPageRepository: DisplayPageRepository,
    private val displaySectionRepository: DisplaySectionRepository,
    private val productRepository: ProductRepository,
    private val eventBannerScheduleRepository: EventBannerScheduleRepository,
    private val recommendationSaaSClient: RecommendationSaaSClient
) {
    fun getHome(): HomeResponse
    // 1. is_home=true && status=PUBLISHED 페이지 조회, 없으면 HomeNotConfiguredException
    // 2. resolveSections(page) 호출(2026-11-09, getDisplayPage와 공유하는 private 메서드로 추출)

    fun getDisplayPage(slug: String): DisplayPageViewResponse
    // (2026-11-09 신설, DBA §2.15) findBySlug(slug) — 없거나 status!=PUBLISHED거나
    // is_exposed=false면 DisplayPageNotFoundException(404). 조회 가능하면 resolveSections(page)
    // 재사용 — getHome()과 동일한 로직, 대상 페이지를 찾는 조건만 다름(is_home=true vs slug=?)

    private fun resolveSections(page: DisplayPage): List<SectionContent>
    // (2026-11-09 추출) 섹션을 sortOrder 순으로 조회 후 종류별 resolve:
    //    - PRODUCT_LIST: content.productIds로 상품 조회 (§11 ProductQueryService.getMobileProducts와 동일 조회 방식)
    //    - EVENT_LIST: content.eventKeys로 eventBannerScheduleRepository에서 조회시점(now) 유효 배너만 조회
    //      (동기화 안 됐거나 기간 경과한 key는 결과에서 조용히 제외, Human Review)
    //    - RECOMMENDATION: recommendationSaaSClient.getRecommendations() 실시간 호출, 실패 시 빈 배열
    //    - BANNER/CATEGORY_GRID/CUSTOM_HTML: content_json 그대로 반환(자체 완결형)
    // getHome()·getDisplayPage() 둘 다 이 메서드를 호출(DBA §2.15 "홈과 완전히 동일")
}
```

### EventBannerScheduleService

```kotlin
@Service
@Transactional
class EventBannerScheduleService(
    private val eventBannerScheduleRepository: EventBannerScheduleRepository
) {
    fun upsertBanner(sourceEventId: String, bannerImageUrl: String, title: String?, linkTarget: String?, startAt: Instant, endAt: Instant?)
    // PROMOTION_EXHIBITION_BANNER_SYNCED 수신 처리. 사전 등록 가능(startAt 미래 허용)
    // [Human Review] Promotion이 실제로 이 이벤트를 발행하는지 미확인 (DBA §7.5)

    fun cancelBanner(sourceEventId: String)
    // PROMOTION_EXHIBITION_BANNER_SYNC_CANCELLED 수신 처리. endAt=now로 종료(물리 삭제 아님)
}
```

### InternalProductController / InternalSkuController

```kotlin
@RestController
@RequestMapping("/api/internal/v1/products")
class InternalProductController(
    private val productQueryService: ProductQueryService,
    private val priceScheduleService: PriceScheduleService
) {
    @GetMapping("/{productId}")
    fun getProductInfo(@PathVariable productId: String): ApiResponse<ProductInfo>
    // Order 연동. priceSale은 조회시점 유효 PriceSchedule JOIN

    @GetMapping("/{productId}/vendor-shipping")
    fun getVendorShipping(@PathVariable productId: String): ApiResponse<VendorShippingInfo>
    // Order 연동. 묶음배송·배송비 계산은 Order가 수행

    @GetMapping("/{productId}/promotion-grouping")
    fun getPromotionGrouping(@PathVariable productId: String): ApiResponse<PromotionGroupingInfo>
    // Promotion 연동. 그룹 판정은 Promotion이 수행

    @GetMapping("/{productId}/max-order-quantity")
    fun getMaxOrderQuantity(@PathVariable productId: String): ApiResponse<MaxOrderQuantityInfo>
    // Promotion 연동(2026-11-09 소급 반영). null=무제한, 실제 필터링은 Promotion이 수행 (REQ-CAT-059b)

    @PostMapping("/{productId}/price-schedule")
    fun registerOrCancelPriceSchedule(
        @PathVariable productId: String,
        @RequestBody request: PriceScheduleActionRequest
    ): ApiResponse<PriceScheduleResponse>
    // Promotion 연동 동기 호출 — PriceScheduleService 로직을 동기 호출로도 제공(배치 지연 시 즉시 반영용)
}

@RestController
@RequestMapping("/api/internal/v1/skus")
class InternalSkuController(
    private val stockService: StockService
) {
    @PostMapping("/{skuId}/reserve")
    fun reserve(
        @PathVariable skuId: String,
        @RequestBody request: ReserveRequest
    ): ApiResponse<StockChangeResponse>

    @GetMapping("/availability")
    fun getAvailability(@RequestParam skuIds: List<String>): ApiResponse<AvailabilityResponse>
}
```

### RecommendationSaaSClient

```kotlin
interface RecommendationSaaSClient {
    fun getRecommendations(productId: String? = null): List<RecommendedProduct>
    // productId 없으면 홈 화면용 일반 추천, 있으면 상품상세 연관상품 추천 (REQ-CAT-036)
    // 외부 SaaS 응답 지연·실패 시 빈 리스트 반환(호출부에서 처리, Human Review: 검증필터·실패처리 미확정)
}
```

### CatalogEventPublisher / Listener

```kotlin
@Component
class CatalogEventPublisher(private val outboxRepository: OutboxRepository) {
    fun publish(event: CatalogDomainEvent)
    // Outbox 패턴(C5 §5.1) — 비즈니스 트랜잭션과 동일 커밋. publish 대상:
    // ProductCreated, ProductApproved, ProductDirectListed, ProductRejected,
    // ProductUpdated, StockChanged
}

@Component
class StockEventListener(
    private val processedEventRepository: ProcessedEventRepository,
    private val stockService: StockService
) {
    @EventListener
    fun onOrderCancelled(event: OrderCancelledEvent)
    // 멱등 검증 후 stockService.restore(..., RESTORE_ORDER_CANCEL)

    @EventListener
    fun onReturnExchangeConfirmed(event: ReturnExchangeConfirmedEvent)
    // 멱등 검증 후 stockService.restore(..., RESTORE_RETURN_EXCHANGE)
}

@Component
class PromotionPriceEventListener(
    private val processedEventRepository: ProcessedEventRepository,
    private val priceScheduleService: PriceScheduleService
) {
    @EventListener
    fun onPromotionPriceScheduled(event: PromotionPriceScheduledEvent)

    @EventListener
    fun onPromotionPriceScheduleCancelled(event: PromotionPriceScheduleCancelledEvent)
}

@Component
class ExhibitionBannerEventListener(
    private val processedEventRepository: ProcessedEventRepository,
    private val eventBannerScheduleService: EventBannerScheduleService
) {
    @EventListener
    fun onExhibitionBannerSynced(event: ExhibitionBannerSyncedEvent)
    // [Human Review] Promotion 실제 발행 여부 미확인

    @EventListener
    fun onExhibitionBannerSyncCancelled(event: ExhibitionBannerSyncCancelledEvent)
}

@Component
class MemberEventListener(
    private val processedEventRepository: ProcessedEventRepository,
    private val wishlistService: WishlistService
) {
    @EventListener
    fun onMemberWithdrawn(event: MemberWithdrawnEvent)
    // 멱등 검증 후 wishlistService.deleteAllByMember(event.memberId) 호출
    // (2026-11-09 소급 반영, DBA §1.14, REQ-CAT-062, PGM: CSM-CAT-008)
    // [Human Review] Member가 이 이벤트(또는 동등한 이벤트)를 실제로 발행하는지 미확인
    // (DBA §6 HR #35, DD HR #10, DI HR #6과 동일 쟁점)
}
```

---

## 3. Catalog 도메인 — 엔티티

### Product

```kotlin
@Entity
@Table(name = "cat_product")
class Product(
    @Id val id: String,
    var name: String,
    val vendorId: String,
    val isDirectSourced: Boolean,
    var categoryId: String,
    var brandId: String? = null,
    var status: ProductStatus,
    var rejectReason: String? = null,
    var rejectCount: Int = 0,
    var rejectedAt: Instant? = null,
    var priceOriginal: Int,
    var priceSupply: Int,
    var releaseDate: LocalDate? = null,
    var description: String? = null,
    var exposureMdOverride: Int? = null,
    var exposureAiScore: BigDecimal? = null,
    var maxOrderQuantity: Int? = null,  // 1회 주문 최대수량, nullable=무제한 (2026-11-09 소급 반영, REQ-CAT-059b)
    val createdAt: Instant,
    var updatedAt: Instant,
    var isDeleted: Boolean = false
) {
    // 판매가(price_sale)는 이 엔티티의 필드가 아니다 — ProductPriceSchedule에서 조회시점 resolve (DBA §4.1-1)

    fun submitForReview() { this.status = ProductStatus.REVIEW_REQUESTED }
    fun startReview() { this.status = ProductStatus.UNDER_REVIEW }
    fun approve() { this.status = ProductStatus.ON_SALE }
    fun reject(reason: String) {
        this.status = ProductStatus.REJECTED
        this.rejectReason = reason
        this.rejectCount += 1
        this.rejectedAt = Instant.now()
    }
    fun resubmit() { this.status = ProductStatus.DRAFT }
    fun markSoldOut() { this.status = ProductStatus.SOLD_OUT }
    fun markOnSaleFromRestock() { this.status = ProductStatus.ON_SALE }  // 대안A, MD 확인 불필요
    fun discontinue() { this.status = ProductStatus.DISCONTINUED }

    fun isResubmitDeadlineExpired(): Boolean =
        status == ProductStatus.REJECTED && rejectedAt != null &&
        Duration.between(rejectedAt, Instant.now()).toDays() > 30

    fun isEscalationTarget(): Boolean = rejectCount >= 3
}

enum class ProductStatus {
    DRAFT, REVIEW_REQUESTED, UNDER_REVIEW, ON_SALE, SOLD_OUT, DISCONTINUED, REJECTED
}
// REVIEW_REQUESTED/UNDER_REVIEW/REJECTED는 isDirectSourced=false 전용 (DF 불변식)
```

### ProductImage / ProductOptionGroup / ProductOptionValue

```kotlin
@Entity
@Table(name = "cat_product_image")
class ProductImage(
    @Id val id: String,
    val productId: String,
    val imageUrl: String,
    var sortOrder: Int = 0,
    val imageType: ImageType = ImageType.DETAIL,
    val createdAt: Instant
)
enum class ImageType { MAIN, DETAIL, THUMBNAIL }
// 상품당 10장 제한은 ProductService에서 검증 (COUNT 쿼리)

@Entity
@Table(name = "cat_product_option_group")
class ProductOptionGroup(
    @Id val id: String,
    val productId: String,
    var name: String,
    val depth: Int,  // 1 또는 2
    var sortOrder: Int = 0,
    val createdAt: Instant
)

@Entity
@Table(name = "cat_product_option_value")
class ProductOptionValue(
    @Id val id: String,
    val optionGroupId: String,
    var value: String,
    var sortOrder: Int = 0,
    val createdAt: Instant
)
```

### ProductWishlist (2026-11-09 소급 반영)

```kotlin
@Entity
@Table(name = "cat_product_wishlist")
class ProductWishlist(
    @Id val id: String,
    val productId: String,
    val memberId: String,
    val createdAt: Instant
)
// unique(productId, memberId) — 상품당 회원 1건 (DBA §1.14)
// 삭제는 물리 삭제(hard delete)만 사용 — 상태 플래그 없음. 상품이 SOLD_OUT/DISCONTINUED로
// 전환되면 WishlistService.deleteAllByProduct가 전체 삭제, 재입고돼도 복원하지 않음 (REQ-CAT-062)
```

### Sku / StockHistory / RestockSubscription

```kotlin
@Entity
@Table(name = "cat_sku")
class Sku(
    @Id val id: String,
    val productId: String,
    val optionValuesJson: String? = null,
    var stockQuantity: Int = 0,
    var availableQuantity: Int = 0,
    val skuCode: String? = null,
    val createdAt: Instant,
    var updatedAt: Instant
) {
    fun reserve(quantity: Int) {
        require(availableQuantity >= quantity) { "INSUFFICIENT_STOCK" }
        availableQuantity -= quantity
    }
    fun restore(quantity: Int) { availableQuantity += quantity }
    fun setStock(quantity: Int) { stockQuantity = quantity; availableQuantity = quantity }
    fun isSoldOut(): Boolean = availableQuantity == 0
}

@Entity
@Table(name = "cat_stock_history")
class StockHistory(
    @Id val id: String,
    val skuId: String,
    val changeType: StockChangeType,
    val changeQuantity: Int,
    val afterStock: Int,
    val afterAvailable: Int,
    val reasonRef: String? = null,
    val createdAt: Instant
)

@Entity
@Table(name = "cat_product_sales_hourly")
@IdClass(ProductSalesHourlyId::class)
class ProductSalesHourly(
    @Id val productId: String,
    @Id val saleHour: Instant,  // 시간 단위 truncate(Asia/Seoul 기준)
    var quantity: Int = 0
)
// 복합키(productId, saleHour). 쓰기는 ProductSalesRankingListener가 원자적 upsert로만 수행
// (2026-11-09 신설, DBA §1.17). sold_quantity_total(Sku 소유, 전체기간 누적)과는 별도 지표

@Entity
@Table(name = "cat_restock_subscription")
class RestockSubscription(
    @Id val id: String,
    val skuId: String,
    val customerId: String,
    var status: SubscriptionStatus = SubscriptionStatus.PENDING,
    val createdAt: Instant,
    var notifiedAt: Instant? = null
) {
    fun notify() { this.status = SubscriptionStatus.NOTIFIED; this.notifiedAt = Instant.now() }
}
enum class SubscriptionStatus { PENDING, NOTIFIED }
```

### ProductPriceSchedule

```kotlin
@Entity
@Table(name = "cat_product_price_schedule")
class ProductPriceSchedule(
    @Id val id: String,
    val productId: String,
    val price: Int,
    val sourceType: PriceSourceType,
    val sourceEventId: String? = null,  // sourceType=BASE면 null
    val startAt: Instant,
    var endAt: Instant? = null,
    val createdBy: String,
    val createdAt: Instant
) {
    fun terminate() { this.endAt = Instant.now() }
    fun isValidAt(now: Instant): Boolean =
        startAt <= now && (endAt == null || endAt!! > now)
}
enum class PriceSourceType { BASE, PROMOTION_EVENT, QUANTITY_DISCOUNT }
// 유효 가격 조회: WHERE productId=? AND startAt<=now AND (endAt IS NULL OR endAt>now)
// 중복 시 판정 규칙은 Human Review (DF #6, DBA §4.1-1)
```

### Category / CategoryAttribute / DisplayCategory / Brand

```kotlin
@Entity
@Table(name = "cat_category")
class Category(
    @Id val id: String,
    var name: String,
    var sortOrder: Int = 0,
    var isActive: Boolean = true,
    val createdAt: Instant,
    var updatedAt: Instant
)
// 단일 계층(대분류만) — parentId 없음 (DBA §3.1)

@Entity
@Table(name = "cat_category_attribute")
class CategoryAttribute(
    @Id val id: String,
    val categoryId: String,
    val attributeName: String,
    val isRequired: Boolean = true,
    var sortOrder: Int = 0
)

@Entity
@Table(name = "cat_display_category")
class DisplayCategory(
    @Id val id: String,
    val parentId: String? = null,
    var name: String,
    val depth: Int = 1,
    var sortOrder: Int = 0,
    var isActive: Boolean = true,
    val createdAt: Instant,
    var updatedAt: Instant
)

@Entity
@Table(name = "cat_brand")
class Brand(
    @Id val id: String,
    var name: String,
    var logoUrl: String? = null,
    var isActive: Boolean = true,
    val createdAt: Instant,
    var updatedAt: Instant
)

@Entity
@Table(name = "cat_product_display_category")
class ProductDisplayCategory(      // 2026-11-09 신설
    @Id val id: String,
    val productId: String,
    val displayCategoryId: String,
    var isAutoMapped: Boolean = false,
    var sortOrder: Int = 0,
    var isPinned: Boolean = false,
    val createdAt: Instant
)
// cat_standard_display_category_mapping(표준-전시 카테고리 자동매핑 기준) 엔티티는
// 상품 등록 시 자동 매핑 로직이 아직 구현되지 않아 별도 작업으로 남김(DF-ERD만 존재)
```

### DisplayPage / DisplaySection / DisplayTemplate

```kotlin
@Entity
@Table(name = "cat_display_page")
class DisplayPage(
    @Id val id: String,
    var title: String,
    val slug: String,
    var status: DisplayPageStatus,
    var templateId: String? = null,
    var isHome: Boolean = false,          // 2026-10-26 신설 (REQ-CAT-052)
    var displayStartAt: Instant? = null,   // 전시 시작일시(2026-11-09 신설, 舊 scheduledAt)
    var displayEndAt: Instant? = null,     // 전시 종료일시(2026-11-09 신설)
    var publishedAt: Instant? = null,
    var closedAt: Instant? = null,
    val createdBy: String,
    val createdAt: Instant,
    var updatedAt: Instant
) {
    fun publish() { this.status = DisplayPageStatus.PUBLISHED; this.publishedAt = Instant.now() }
    fun updateContent(title: String?, startAt: Instant?, endAt: Instant?) {
        require(endAt == null || startAt == null || endAt.isAfter(startAt)) { "INVALID_DISPLAY_PERIOD" }
        title?.let { this.title = it }; this.displayStartAt = startAt; this.displayEndAt = endAt
    }  // 상태 전이 없음. DRAFT·PUBLISHED 공통(2026-11-09, 舊 schedule/startEdit/republish 통합)
    fun close() { this.status = DisplayPageStatus.CLOSED; this.closedAt = Instant.now(); this.isHome = false }

    fun setAsHome() {
        require(status == DisplayPageStatus.PUBLISHED) { "INVALID_STATUS" }
        this.isHome = true
    }
    fun unsetHome() { this.isHome = false }
}
enum class DisplayPageStatus { DRAFT, PUBLISHED, CLOSED, CANCELLED }  // 2026-11-09: DRAFT_EDIT·SCHEDULED·RESERVED 제거

@Entity
@Table(name = "cat_display_section")
class DisplaySection(
    @Id val id: String,
    val pageId: String,
    val sectionType: SectionType,
    var title: String? = null,
    var contentJson: String? = null,
    // PRODUCT_LIST={productIds:[]} / EVENT_LIST={eventKeys:[]} / RECOMMENDATION=null / BANNER=자체 이미지URL+링크
    var sortOrder: Int = 0,
    val createdAt: Instant,
    var updatedAt: Instant
)
enum class SectionType { BANNER, PRODUCT_LIST, CATEGORY_GRID, CUSTOM_HTML, EVENT_LIST, RECOMMENDATION }
// EVENT_LIST·RECOMMENDATION은 2026-10-26 추가 (DBA §6.4-1)

@Entity
@Table(name = "cat_display_template")
class DisplayTemplate(
    @Id val id: String,
    var name: String,
    var layoutJson: String,
    var isActive: Boolean = true,
    val createdAt: Instant,
    var updatedAt: Instant
)
// 관리 화면 미설계(보류) — DE-메뉴구조도/admin.md "템플릿" 메뉴 Human Review 참조
```

### EventBannerSchedule

```kotlin
@Entity
@Table(name = "cat_event_banner_schedule")
class EventBannerSchedule(
    @Id val id: String,
    val sourceEventId: String,  // Promotion prm_exhibition.id 참조값 (FK 강제 없음)
    var bannerImageUrl: String,
    var title: String? = null,
    var linkTarget: String? = null,
    val startAt: Instant,
    var endAt: Instant? = null,
    val createdAt: Instant,
    var updatedAt: Instant
) {
    fun terminate() { this.endAt = Instant.now() }
    fun isValidAt(now: Instant): Boolean = startAt <= now && (endAt == null || endAt!! > now)
}
// 2026-11-04 신설. [Human Review] Promotion 측 동기화 이벤트 발행 여부 미확인 (DBA §7.5)
```

### GnbMenu (2026-11-09 신설)

```kotlin
@Entity
@Table(name = "cat_gnb_menu")
class GnbMenu(
    @Id val id: String,
    var name: String,
    var linkType: GnbLinkType,
    var linkTarget: String,
    var sortOrder: Int = 0,
    var isExposed: Boolean = true,
    var displayStartAt: Instant? = null,
    var displayEndAt: Instant? = null,
    val createdBy: String,
    val createdAt: Instant,
    var updatedAt: Instant
) {
    fun isCurrentlyExposed(now: Instant): Boolean =
        isExposed &&
        (displayStartAt == null || !displayStartAt!!.isAfter(now)) &&
        (displayEndAt == null || displayEndAt!!.isAfter(now))
}
// 단일 계층(서브메뉴 없음). linkType==EVENT_PAGE/EXTERNAL_URL은 linkTarget을 URL 문자열로
// 그대로 저장(검증 없음, cat_event_banner_schedule.link_target과 동일 패턴). 홈 화면 전용
// 노출(DBA §2.14) — PC 채널 생기면 노출 범위 재검토
```

---

## 근거

| 항목 | 출처 |
|---|---|
| 클래스 도출 | `deliverables/S3-상세설계/DM-시퀀스/catalog.md` 참여 객체(§1~16) |
| 메서드 시그니처 | `deliverables/S3-상세설계/DL-인터페이스명세/catalog.md` 34개 endpoint |
| 패키지 구조 | `deliverables/S1-범위정의/D9-컴포넌트.md` 도메인 모듈 구조, Order(`DP-클래스설계/order.md`)와 동일 서브도메인 분리 패턴 |
| 엔티티 속성 | `deliverables/S2-구조설계/DF-도메인모델ERD/catalog.md` 전체 테이블(cat_product~cat_event_banner_schedule) |
| 상태 전이 메서드 | `deliverables/S2-구조설계/DH-상태머신/catalog.md` |
| 재고 자동전환(대안A) 공통화(`applyAutoTransition`) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §2.4 — DM §6·§8 두 경로가 동일 로직을 쓰는 것을 메서드 추출로 반영 |
| 판매가 분리(PriceService/PriceScheduleService) | ADR-C001, DBA §4.1-1 |
| 직매입/입점형 단일 테이블(Product.isDirectSourced) | ADR-C002 |
| 출시일 노출 게이트 | ADR-C003, DD REQ-CAT-033~034 |
| 재고 복원 자동전환 | ADR-C004 |
| 이벤트 배너 동기화 | ADR-C005, DD REQ-CAT-054~055 — Human Review 전제 명시 |
| 이벤트 처리(Outbox) | `deliverables/S2-구조설계/DI-이벤트플로우/catalog.md` 이벤트 운영 규칙 |
| 홈 화면 지정·조회 | DD REQ-CAT-052~053, DBA §6.4·§6.4-1 |
| 전시카테고리 상품순서(ProductDisplayCategory.sortOrder/isPinned) | DD REQ-CAT-071~072, DBA §2.5.3(2026-11-09 신설) |
| 고객 상품 목록·검색 카테고리 기준 변경, 카테고리 메뉴 트리 조회 | DD REQ-CAT-029·031·073, DBA §2.5.1~§2.5.2(2026-11-09 재정의) |
| 복제등록(ProductService.duplicate)·대량등록(bulkCreate) | DD REQ-CAT-056~057, DBA §1.5.2~§1.5.3 — 2026-11-09 소급 반영 |
| 찜하기(WishlistService, ProductWishlist 엔티티) | DD REQ-CAT-061~062, DBA §1.14 — 2026-11-09 소급 반영 |
| SNS 공유(ProductQueryService.getShareMetadata, DisplayPageService.getShareMetadata) | DD REQ-CAT-063, DBA §1.16 — 2026-11-09 소급 반영 |
| 주문 수량 제한(Product.maxOrderQuantity, InternalProductController.getMaxOrderQuantity) | DD REQ-CAT-059b, DBA §1.8 — 2026-11-09 소급 반영 |
| 상품 랭킹(ProductSalesHourly, ProductSalesRankingListener의 StockChanged 내부 재구독, MobileRankingController) | DD REQ-CAT-074~075, DBA §1.17·§2.13(2026-11-09 신설), `DI-이벤트플로우/catalog.md` 도메인 내부 이벤트 |
| 찜 데이터 정리(MemberEventListener, WishlistService.deleteAllByMember) | DD REQ-CAT-062, DBA §1.14·§6 HR #35 — 2026-11-09 소급 반영(PGM: CSM-CAT-008) |
| admin 전용 가격변경(AdminProductController.changePrice, PriceService.changePrice actorId 일반화) | DD REQ-CAT-026(본문 보강), DBA §1.7.1 — 2026-11-09 신설(PGM: API-CAT-043, DQ 미진항목 #2 해소) |
| admin 전용 이미지·옵션 등록(AdminProductController.addImage/setOptions) | DK §5 — 2026-11-09 소급 반영(PGM: API-CAT-044~045, DQ 미진항목 #1 해소) |
| GNB 메뉴 관리(GnbMenu, GnbMenuService, AdminGnbMenuController, MobileGnbMenuController) | DD REQ-CAT-076~077, DBA §2.14 — 2026-11-09 신설(PGM: API-CAT-046~047, SCR-A-C11) |
| 비홈 전시 페이지 뷰어(HomeQueryService.getDisplayPage/resolveSections 추출, MobileDisplayPageController.getDisplayPage) | DD REQ-CAT-078, DBA §2.15 — 2026-11-09 신설(PGM: API-CAT-048, SCR-M-C07, 미진항목 #9·#13 해소) |
| 상품 요약·태그(Product.summary/tags, 신규 컬럼) | DD REQ-CAT-079, DBA §1.3.3·§1.3.4(기존 정책) — 2026-11-09 소급 반영 |
| 옵션값 이미지(ProductOptionValue.imageUrl, ProductOptionService.uploadOptionImage, Admin/PartnerProductController.uploadOptionImage) | DD REQ-CAT-080~081, DBA §1.4.1 — 2026-11-09 신설(PGM: API-CAT-049 partner·050 admin, DL §45) |
| 상품 단위 전시여부·검색노출 제외(Product.isExposed/isSearchExcluded, ProductService.updateBasicInfo 확장, ProductQueryService 조회 게이트) | DD REQ-CAT-082~083, DBA §2.16 — 2026-11-09 신설. SCR-A-C04-T6(전시 탭) 폐지, 기본정보 탭 PATCH API로 통합, 신규 API-CAT 번호 없음 |
