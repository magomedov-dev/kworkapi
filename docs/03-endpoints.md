# Каталог эндпоинтов kwork API

> Сгенерировано автоматически из декомпилированного приложения `research/extract_endpoints.py`. Базовый URL: `https://api.kwork.ru/`.

Все методы — `application/x-www-form-urlencoded`. Общие поля у большинства: `token`, `uad`, `slrememberme`, `device`; заголовки `Authorization` (статичный) и `Cookie`.


## ActorService (49)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `addPhoneNumber` | POST | `/addPhoneNumber` | `phone` | — |
| `allowMobilePush` | POST | `/allowMobilePush` | `allow` | — |
| `changeEmail` | POST | `/emailVerificationLetter` | `email` | — |
| `changePassword` | POST | `/changePassword` | `password` | — |
| `changePayerSubRole` | POST | `/changePayerSubRole` | `payerSubRole` | — |
| `changeUsername` | POST | `/changeUsername` | `username` | — |
| `deleteAccount` | POST | `/deleteAccount` | — | — |
| `fcmNotificationsRead` | POST | `/fcmNotificationsRead` | `messageIds[]` | — |
| `fcmNotificationsReceived` | POST | `/fcmNotificationsReceived` | `messageIds[]`, `makeOnline` | — |
| `getActor` | POST | `/actor` | `isAppWhiteListed`, `whiteListedLastShowTime`, `whiteListedWindowSkipped`, `isAppPushOn`, `appPushOnLastShowTime`, `makeOnline` | — |
| `getAvailableFeatures` | POST | `/getAvailableFeatures` | — | — |
| `getBadgesInfo` | POST | `/getBadgesInfo` | `makeOnline` | — |
| `getBillRefillUrl` | POST | `/getBillRefillUrl` | `sum` | — |
| `getCaptchaStatus` | POST | `/getCaptchaStatus` | — | — |
| `getChannel` | POST | `/getChannel` | `makeOnline` | — |
| `getCitiesResponse` | POST | `/cities` | `countryId` | — |
| `getCountriesResponse` | POST | `/countries` | — | — |
| `getInfoByTaxNumber` | POST | `/getCompanyDetails` | `tax_number` | — |
| `getPaymentMethods` | POST | `/getPaymentMethods` | `withCompany` | — |
| `getPublicFeatures` | POST | `/getPublicFeatures` | — | — |
| `getSecurityUserData` | POST | `/getSecurityUserData` | — | — |
| `getTimeZonesResponse` | POST | `/timezones` | — | — |
| `getWebAuthToken` | POST | `/getWebAuthToken` | `url_to_redirect` | — |
| `hideVoiceMessageSettingsPopup` | POST | `/hideVoiceMessageSettingsPopup` | — | — |
| `isDialogAllow` | POST | `/isDialogAllow` | `receiverId` | — |
| `logOut` | POST | `/logout` | `pushToken` | — |
| `notificationsFetch` | POST | `/notificationsFetch` | `page`, `makeOnline` | — |
| `notificationsReceived` | POST | `/notificationsReceived` | `ids[]`, `makeOnline` | — |
| `registerCloudToken` | POST | `/registerCloudToken` | `cloud_token`, `os`, `app_version` | — |
| `registerCloudTokenError` | POST | `/fcmTokenRequestFailed` | `cancel_reason`, `os`, `app_version` | — |
| `resetPassword` | POST | `/resetPassword` | `email`, `g-recaptcha-response` | — |
| `sendCompanyForVerification` | POST | `/sendCompanyForVerification` | `tax_number`, `address` | — |
| `sendSelfEmployedSurveyResult` | POST | `/sendSelfEmployedSurveyResult` | `answer` | — |
| `sendWhatsappCode` | POST | `/sendWhatsAppCode` | `phone`, `hash` | — |
| `setNotifyCardRefill` | POST | `/setNotifyCardRefill` | `flag` | — |
| `setTakingOrders` | POST | `/setTakingOrders` | `status` | — |
| `setUserRole` | POST | `/setUserType` | `type` | — |
| `setVoiceMessageReceiving` | POST | `/setVoiceMessageReceiving` | `is_allowed` | — |
| `setVoiceMessageSpeed` | POST | `/setVoiceMessageSpeed` | `speed` | — |
| `signIn` | POST | `/signIn` | `login`, `password`, `recaptcha_pass_token` | — |
| `signInWithCaptcha` | POST | `/signIn` | `login`, `password`, `g-recaptcha-response`, `recaptcha_pass_token`, `phone_last` | — |
| `signUp` | POST | `/signUp` | `username`, `email`, `password`, `type`, `promocode`, `g-recaptcha-response`, `is_subscribed` | — |
| `socialSignInByToken` | POST | `/socialSignInByTokenv2` | — | Body(JSON) |
| `socialSignUpByToken` | POST | `/socialSignUpByToken` | `provider`, `email`, `user_type`, `promocode`, `is_subscribed` | — |
| `updateAvatar` | POST | `/updateAvatar` | — | Multipart |
| `updateSettings` | POST | `/updateSettings` | `username`, `fullname`, `timezoneId`, `email`, `countryId`, `cityId`, `details`, `profession`, `is_consent` | — |
| `validateEvent` | POST | `/validateEvent` | `id` | — |
| `verifyPhoneActivationCode` | POST | `/verifyPhoneActivationCode` | `code` | — |
| `verifySmsCodeForAccountDeleting` | POST | `/verifySmsCodeForAccountDeleting` | `code` | — |

## CatalogService (12)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `catalogFilters` | POST | `/catalogFilters` | `categoryId`, `classifierId`, `isSearch`, `query`, `unembedded` | FieldMap |
| `getCatalogCategories` | POST | `/catalogCategories` | `rubricId` | — |
| `getCatalogMainData` | POST | `/catalogMain` | — | — |
| `getCatalogMainDataV2` | POST | `/catalogMainv2` | — | — |
| `getCatalogRubrics` | POST | `/catalogRubrics` | — | — |
| `getFavoriteKworks` | POST | `/favoriteKworks` | `page` | — |
| `getHiddenKworks` | POST | `/getHiddenKworks` | `page` | — |
| `getKworks` | POST | `/kworks` | `categoryId`, `classifierId`, `excluded`, `unembedded`, `page`, `limit` | FieldMap |
| `getViewedKworks` | POST | `/viewedCatalogKworks` | `page` | — |
| `searchKworks` | POST | `/search` | `query`, `categoryId`, `classifierId`, `excluded`, `unembedded`, `page`, `limit` | FieldMap |
| `searchKworksCatalogQuery` | POST | `/searchKworksCatalogQuery` | `query`, `page` | — |
| `userSearch` | POST | `/userSearch` | `query`, `page` | — |

## DialogService (8)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `deleteDialog` | POST | `/hideDialog` | `userId`, `isRestore` | — |
| `getDialog` | POST | `/getDialog` | `id`, `makeOnline`, `withTracks` | — |
| `getDialogs` | POST | `/dialogs` | `page`, `filter`, `makeOnline`, `withTracks` | — |
| `getQuizQuestions` | POST | `/getFishingTutorialQuestions` | `makeOnline` | — |
| `readDialog` | POST | `/inboxRead` | `user_id` | — |
| `sendQuizResult` | POST | `/setFishingTutorialStatus` | `status`, `makeOnline` | — |
| `setDialogStarred` | POST | `/setDialogStarred` | `userId`, `isStarred` | — |
| `unreadDialog` | POST | `/unreadDialog` | `user_id` | — |

## ExchangeService (14)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `categories` | POST | `/categories` | `type` | — |
| `deleteOffer` | POST | `/deleteOffer` | `id` | — |
| `deleteWant` | POST | `/deleteWant` | — | Body(JSON) |
| `exchangeInfo` | POST | `/exchangeInfo` | — | Body(JSON) |
| `favoriteCategories` | POST | `/favoriteCategories` | — | — |
| `getConnects` | POST | `/projects` | `categories`, `price_to`, `page` | — |
| `getMyOffers` | POST | `/offers` | `page` | — |
| `getOffer` | POST | `/offer` | `id` | — |
| `getProjectsCount` | POST | `/getWantsCount` | `categories`, `attributes`, `price_from`, `price_to`, `hiring_from`, `offers` | — |
| `getWorkerProjects` | POST | `/projects` | `categories`, `attributes`, `price_from`, `price_to`, `hiring_from`, `offers`, `query`, `page` | — |
| `restartWant` | POST | `/restartWant` | — | Body(JSON) |
| `setFavorites` | POST | `/setFavorite` | `categories`, `attributes` | — |
| `stopWant` | POST | `/stopWant` | — | Body(JSON) |
| `wantsStatusList` | POST | `/wantsStatusList` | — | Body(JSON) |

## FileService (3)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `getOrderFiles` | POST | `/getOrderFiles` | `id` | — |
| `getVoiceMessageConvertStatus` | POST | `/getVoiceMessageConvertStatus` | `file_id` | — |
| `markVoiceMessageHeard` | POST | `/markVoiceMessageHeard` | `conversation_id` | — |

## InboxService (12)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `getInboxList` | POST | `/getInboxTracks` | `userId`, `page`, `lastConversationId`, `limit`, `direction`, `makeOnline` | — |
| `getMessage` | POST | `/inboxTrackMessage` | `conversationId` | — |
| `getVoiceMessageTranscription` | POST | `/getVoiceMessageTranscription` | `conversation_id` | — |
| `inboxComplainMessage` | POST | `/inboxComplainMessage` | `message_id`, `comment` | — |
| `inboxCreate` | POST | `/inboxCreate` | `user_id`, `message_key`, `text`, `reply_message_id`, `kwork_id` | — |
| `inboxDelete` | POST | `/inboxDelete` | `id` | — |
| `inboxEdit` | POST | `/inboxEdit` | `id`, `text`, `reply_message_id` | — |
| `inboxMessage` | POST | `/inboxMessage` | `messageId`, `makeOnline` | — |
| `markInboxTracksAsRead` | POST | `/markInboxTracksAsRead` | `userId`, `conversationIds[]` | — |
| `offline` | POST | `/offline` | — | — |
| `searchInboxes` | POST | `/searchMessages` | `text`, `userId`, `page` | — |
| `sendInteractionStatus` | POST | `/sendUserStatus` | `user_id`, `orderId`, `status` | — |

## KworkDetailsService (10)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `createKworkComplain` | POST | `/createKworkComplain` | — | Body(JSON) |
| `getComplainCategories` | POST | `/getComplainCategories` | — | — |
| `getFaq` | POST | `/getKworkAnswers` | `id` | — |
| `getKworkDetails` | POST | `/getKworkDetails` | `id` | — |
| `getKworkDetailsExtra` | POST | `/getKworkDetailsExtra` | `id` | — |
| `getKworkLinksTable` | POST | `/getKworkLinksTable` | `id`, `page` | — |
| `getKworkPortfolios` | POST | `/getKworkPortfolios` | `id`, `page` | — |
| `getKworkReviews` | POST | `/getKworkReviews` | `kwork_id`, `type`, `page` | — |
| `orderKwork` | POST | `/orderKwork` | — | Body(JSON) |
| `rechargeBalance` | POST | `/rechargeBalance` | `orderId`, `amount`, `payment_id`, `paymentType`, `country_group_code` | — |

## KworkService (7)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `getInAppNotification` | POST | `/getInAppNotification` | `app_version`, `os_type` | — |
| `getPrivacy` | POST | `/privacy` | — | — |
| `getResolution` | POST | `/resolution` | — | — |
| `getTOS` | POST | `/tos` | — | — |
| `getTerms` | POST | `/terms` | — | — |
| `getTermsOfService` | POST | `/termsOfService` | — | — |
| `sendInAppNotificationAction` | POST | `/pushInAppNotificationLog` | `notificationId`, `action` | — |

## NotificationService (1)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `getNotifications` | POST | `/notifications` | `makeOnline` | — |

## OrderService (50)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `acceptExtraDeleteRequest` | POST | `/workerConfirmsExtraRemovalRequest` | `track_id` | — |
| `acceptExtraOffer` | POST | `/acceptExtras` | `order_id`, `track_id` | — |
| `acceptStageOffer` | POST | `/acceptStageSuggestion` | `order_id` | — |
| `allowPortfolio` | POST | `/allowOrderPortfolioUpload` | `order_id` | — |
| `approveOrder` | POST | `/approveOrder` | `orderId`, `portfolio` | — |
| `approveOrderStages` | POST | `/approveOrderStage` | `orderId`, `stageIds[]` | — |
| `cancelExtraDeleteRequest` | POST | `/payerDeclinesExtraRemovalRequest` | `track_id` | — |
| `cancelExtraOffer` | POST | `/workerDeclineExtras` | `order_id`, `track_id` | — |
| `cancelOrderAsPayer` | POST | `/cancelOrderByPayer` | `order_id`, `reason_type`, `hideKworks`, `message` | — |
| `cancelOrderAsWorker` | POST | `/cancelOrderByWorker` | `order_id`, `reason_type`, `message` | — |
| `cancelOrderAwaitingPayment` | POST | `/cancelOrderAwaitingPayment` | `order_id` | — |
| `confirmCancelRequestAsPayer` | POST | `/confirmCancelOrderRequestByPayer` | `order_id`, `reply_type` | — |
| `confirmCancelRequestAsWorker` | POST | `/confirmCancelOrderRequestByWorker` | `order_id` | — |
| `createAnswer` | POST | `/createAnswer` | `review_id`, `text` | — |
| `createReview` | POST | `/createReview` | `order_id`, `type`, `text` | — |
| `declineExtraDeleteRequest` | POST | `/workerDeclinesExtraRemovalRequest` | `track_id` | — |
| `deleteCancelRequestAsPayer` | POST | `/deleteCancelOrderRequestByPayer` | `order_id` | — |
| `deleteCancelRequestAsWorker` | POST | `/deleteCancelOrderRequestByWorker` | `order_id` | — |
| `deleteExtraAsPayer` | POST | `/payerExtraDelete` | `extra_id` | — |
| `deleteExtraAsWorker` | POST | `/workerExtraDelete` | `extra_id` | — |
| `deletePortfolio` | POST | `/deletePortfolio` | `portfolio_id`, `unlink` | — |
| `deleteReview` | POST | `/deleteReview` | `order_id` | — |
| `editAnswer` | POST | `/editAnswer` | `answer_id`, `text` | — |
| `editReview` | POST | `/editReview` | `order_id`, `type`, `text` | — |
| `getAvailableExtras` | POST | `/getExtrasAvailableForOrder` | `orderId` | — |
| `getCancelReasons` | POST | `/getOrderCancellationReasons` | `orderId` | — |
| `getCustomExtraParams` | POST | `/getCustomOptionsPresets` | `order_id` | — |
| `getOrderDetails` | POST | `/getOrderDetails` | `orderId` | — |
| `getOrderExtras` | POST | `/getOrderedExtras` | `orderId` | — |
| `getOrderHeader` | POST | `/getOrderHeader` | `orderId` | — |
| `getPayerOrders` | POST | `/payerOrders` | `filter`, `company_orders`, `page` | — |
| `getWorkerOrders` | POST | `/workerOrders` | `filter`, `page` | — |
| `offerExtras` | POST | `/offerOrderOptions` | `orderId` | FieldMap |
| `orderExtras` | POST | `/payerBuyExtras` | `order_id`, `as_volume` | FieldMap |
| `orderStage` | POST | `/orderStage` | `order_id`, `stage_id` | — |
| `payOrderAwaitingPayment` | POST | `/payOrderAwaitingPayment` | `order_id` | — |
| `rateArbitration` | POST | `/rateArbitration` | `id`, `rating` | — |
| `rejectCancelRequestAsPayer` | POST | `/rejectCancelOrderRequestByPayer` | `order_id` | — |
| `rejectCancelRequestAsWorker` | POST | `/rejectCancelOrderRequestByWorker` | `order_id` | — |
| `rejectExtraOffer` | POST | `/payerDeclineExtras` | `order_id`, `track_id` | — |
| `rejectStageOffer` | POST | `/rejectStageSuggestion` | `order_id` | — |
| `repeatOrder` | POST | `/repeatOrder` | `orderId` | — |
| `sendBonus` | POST | `/sendBonus` | `orderId`, `bonus`, `comment` | — |
| `sendOrderForApproval` | POST | `/sendOrderForApproval` | `orderId`, `metrics[]`, `stageIds[]` | — |
| `sendOrderForRevision` | POST | `/sendOrderForRevision` | `orderId`, `revision`, `files[]`, `stageIds[]` | — |
| `sendOrderRequirements` | POST | `/sendOrderRequirements` | `orderId`, `requirements`, `files[]`, `metrics[]` | — |
| `sendReceipt` | POST | `/sendOrderReceiptLinkForVerification` | `receiptId`, `receiptLink` | — |
| `sendReport` | POST | `/sendReport` | `order_id`, `progress`, `comment`, `track_id` | — |
| `updateStageProgress` | POST | `/updateStageProgress` | `order_id`, `comment`, `metrics[]`, `trackId` | FieldMap |
| `workerInprogress` | POST | `/workerInprogress` | `order_id`, `contracts_agreement` | — |

## PortfolioService (2)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `portfolioCategoriesList` | POST | `/portfolioCategoriesList` | `user_id` | — |
| `portfolioList` | POST | `/portfolioList` | `user_id`, `category_id`, `page` | — |

## TrackService (7)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `getTracks` | POST | `/getTracks` | `orderId`, `trackId`, `limit`, `direction` | — |
| `getVoiceMessageTranscription` | POST | `/getVoiceMessageTranscription` | `conversation_id` | — |
| `searchTracks` | POST | `/searchOrderTracks` | `text`, `orderId`, `page` | — |
| `trackCreate` | POST | `/inboxCreate` | `user_id`, `message_key`, `order_id`, `text`, `uploaded_files[]`, `reply_message_id`, `withTracks` | — |
| `trackDelete` | POST | `/trackDelete` | `id` | — |
| `trackEdit` | POST | `/trackEdit` | `id`, `quoteId`, `text`, `uploadedFiles[]` | — |
| `trackRead` | POST | `/trackRead` | `ids[]` | — |

## UserService (17)

| Метод | HTTP | Путь | Поля формы | Особое |
|---|---|---|---|---|
| `blockDialog` | POST | `/blockDialog` | `blockUserId` | — |
| `deleteKwork` | POST | `/deleteKwork` | `kwork_id` | — |
| `getActorKworks` | POST | `/userKworks` | `page`, `user_id`, `category_id`, `status_id` | — |
| `getBlockedDialogs` | POST | `/blockedDialogs` | `page` | — |
| `getUserInfo` | POST | `/user` | `id`, `makeOnline` | — |
| `getUserInfo` | POST | `/userByUsername` | `username` | — |
| `getUserKworks` | POST | `/userKworks` | `page`, `user_id`, `category_id`, `status_id` | — |
| `getUserKworksCategories` | POST | `/kworksCategoriesList` | `user_id` | — |
| `kworksStatusList` | POST | `/kworksStatusList` | — | — |
| `markKworkAsFavorite` | POST | `/markKworkAsFavorite` | `kwork_id`, `is_favorite` | — |
| `markKworkAsHidden` | POST | `/markKworkAsHidden` | `kwork_id`, `is_hidden` | — |
| `markKworkForBlackFriday` | POST | `/markKworksBlackFriday` | `kworkId` | — |
| `pauseKwork` | POST | `/pauseKwork` | `kwork_id` | — |
| `setAvailableAtWeekends` | POST | `/setAvailableAtWeekends` | `available` | — |
| `startKwork` | POST | `/startKwork` | `kwork_id` | — |
| `unblockDialog` | POST | `/unblockDialog` | `blockUserId` | — |
| `userReviews` | POST | `/userReviews` | `user_id`, `type`, `page` | — |

---

**Всего эндпоинтов: 192** в 14 сервисах.
