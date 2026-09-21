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
- Feature composables own page-scoped server state such as loading, error, empty, and loaded data.
- Pages compose views and navigation. They do not implement authentication, raw networking, or reusable request-state machinery.
- Components receive data through props and emit user intent; they do not fetch server data.

## Active exam recovery

`useExamStore` writes a versioned `exam_active_progress_v1` snapshot after every meaningful change and when the app enters the background. The snapshot includes:

- paper identity, configuration, and the redacted question payload;
- current question and selected answers;
- successfully submitted questions and known correctness in practice mode;
- selected wrong reasons and accumulated per-question time;
- the absolute paper start time.

Snapshots expire after seven days. Finishing or resetting a paper removes the snapshot. Starting a new paper requires confirmation when unfinished progress exists. Exam countdowns use an absolute deadline so suspended timers catch up after background resume.

The snapshot only contains fields already delivered to the client. Exam-mode answers and analysis remain absent because the backend redacts them.

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

## Adding a feature

1. Add the backend contract or mapping in `api/contracts.ts`.
2. Add domain calls in `features/<domain>/api.ts` using `api/client.ts`.
3. Put reusable page-query behavior in a feature composable using `useAsyncState`.
4. Use Pinia only if state must cross routes or survive app background/resume.
5. Compose the page from shared components and design tokens.
6. Build `mp-weixin` and verify loading, empty, error, retry, background, and resume behavior.
