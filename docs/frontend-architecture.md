# Frontend Architecture

## Source of truth

The active uni-app application lives entirely under `client/src`:

- `App.vue` owns application lifecycle behavior.
- `pages.json` is the only page and navigation manifest.
- `api/client.ts` is the only HTTP and download transport.
- `.env.*.local` selects one API endpoint for the current environment.

Pages and features must not call `uni.request` or concatenate the API base URL directly.

## Layers

```text
pages/          Route entry and view composition
features/       Domain API definitions and page-scoped query composables
stores/         Cross-page durable application state
components/     Reusable visual building blocks
shared/         Domain-neutral composables and UI utilities
api/            Transport and backend contract mapping
types/          Product-facing shared types
constants/      Stable product options and labels
styles/         Global design tokens and foundations
```

Dependencies point downward. Shared code cannot import pages or feature-specific code. A feature may use the transport, contracts, shared utilities, and stores, but one feature should not reach into another feature's internal composable.

## State ownership

- Pinia stores hold state that must survive page changes or app lifecycle transitions. The user store owns authentication and selected exams. The exam store owns the active paper and its recoverable progress.
- Home, practice and profile share `userStore.selectedExams`: zero selections means browsing, one means a single goal, and two means both goals. `ExamSelection` emits independent toggles. `useExamNavigation` asks which exam to practice when there are zero or two goals; the session choice does not change the stored goals. Active paper recovery retains its original exam type.
- Feature composables own page-scoped server state such as loading, error, empty, and loaded data.
- Pages compose views and navigation. They do not implement authentication, raw networking, or reusable request-state machinery.
- Components receive data through props and emit user intent; they do not fetch server data.

## Active exam recovery

`useExamStore` writes a versioned `exam_active_progress_v2` snapshot after every meaningful change and when the app enters the background. The snapshot includes:

- paper identity, configuration, and the redacted question payload;
- current question and selected answers;
- successfully submitted questions and known correctness in practice mode;
- selected wrong reasons and accumulated per-question time;
- the absolute paper start time.

Snapshots expire after seven days. Finishing or resetting a paper removes the snapshot. Starting a new paper requires confirmation when unfinished progress exists. Exam countdowns use an absolute deadline so suspended timers catch up after background resume.

The snapshot only contains fields already delivered to the client. Both modes start with redacted solutions. Practice merges the solution returned by a successful submission; exam solutions appear only in results.

## Shared UI states

`AppState` supplies consistent loading, empty, and retryable error presentation. `confirmAction` supplies promise-based confirmation. Existing `QuestionItem`, `AnswerCard`, `CountdownBar`, and `RingChart` cover question display, answer navigation, timed progress, and result visualization.

New screens should reuse these foundations before adding page-local variants.

## Design tokens

Global `--app-*` tokens in `styles/app.scss` are the source of truth for:

- semantic colors and surfaces;
- typography scale;
- spacing scale;
- radius scale;
- elevation shadows;
- success, warning, and danger states.

Page styles may define layout, but should not introduce a second brand palette or arbitrary replacements for existing token values.

### Approved visual baseline (2026-10-11)

- Background `#F7F1E8`, card surface `#FFFAF3`, primary terracotta `#B86B4B`, charcoal text `#2F2926`, and sage accent `#7E9A80`.
- Use quiet solid surfaces, light borders and shadows, readable sans-serif text, and serif accents for dashboard numbers.
- Keep the native navigation and four tabs: 首页、刷题、AI问答、我的.
- Home prioritizes goals, a resume/start action, live study metrics, review tools and recent practice. News remains a preparation state until real content is available.
- Display HSK in UI text through `getExamLabel` / `getPaperTitle`; preserve the existing `HKS` backend identifier.
- `AppState` supports `compact` for inline cards. Failed data requests should expose retry, not fabricate zero metrics or successful empty lists.
- AI uses a full-width conversation and flex composer. Failed sends retain the draft; new conversations retain previous sessions. Photo controls are deferred until actual image submission is supported.
- Vite uses the already available esbuild minifier, so local builds do not require the absent optional terser package.

## Adding a feature

1. Add the backend contract or mapping in `api/contracts.ts`.
2. Add domain calls in `features/<domain>/api.ts` using `api/client.ts`.
3. Put reusable page-query behavior in a feature composable using `useAsyncState`.
4. Use Pinia only if state must cross routes or survive app background/resume.
5. Compose the page from shared components and design tokens.
6. Build `mp-weixin` and verify loading, empty, error, retry, background, and resume behavior.

## New bank UI (2026-10-22)

Catalog data drives version, level, subject, module and knowledge-point controls. Oral and oral-translation tasks are deferred. QuestionItem supports audio lifecycle, image stems/options, written drafts, explicit submission and self-review. API media paths resolve through the configured API origin. Result pages reuse QuestionItem for complete material and solution review. Objective accuracy and self-assessed scores are displayed independently. Version2 snapshots avoid restoring stale IDs after the database rebuild.

## Profile support pages (1.5.1)

Profile links to a private text-feedback form and a dedicated About page. About contains only the brand icon/name/version/introduction, announcements and the official privacy-guide link. It does not add contact, feedback or applicability notices.

Feedback drafts and idempotency keys are scoped to the current user; retry/reopen preserves the key, editing changes it, and success clears the draft. Native textarea/button controls retain input on failures and prevent duplicate submission. The success state scrolls back to the top after rendering.

Announcements use public paginated API calls with explicit loading/empty/error/retry states and text-only detail rendering. The existing admin page can edit versioned drafts and publish/withdraw them. `APP_VERSION` reads manifest.versionName so About and feedback metadata match the build.

The privacy link invokes `wx.openPrivacyContract` only on WeChat and shows an appropriate fallback elsewhere; no custom privacy-authorization flow is introduced. See [release-1.5.1.md](release-1.5.1.md).
