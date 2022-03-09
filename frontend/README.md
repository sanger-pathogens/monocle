# Monocle's [SvelteKit](https://kit.svelte.dev/) frontend

## Getting started

Have [Node.js](https://nodejs.org) installed.

Install other dependencies:

```bash
cd frontend
npm install
```
## Development

### Running locally

Connect the local FE to the API as per [monocle-developer/FE_development.md#running-the-fe-outside-docker-without-having-to-mock-the-api](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle-developer/-/blob/master/FE_development.md#running-the-fe-outside-docker-without-having-to-mock-the-api).

Afterwards, start the development server:

```bash
npm run dev
```
and navigate to [http://localhost:8080/](http://localhost:8080/) (_note: port `8080`, not `3000`_).

### Running tests

```bash
npm test
```
or in the watch mode:

```bash
npm run test:watch
```

### Linting JS & Svelte code

To display linting issues, run:

```bash
npm run lint
```
To fix linting issues that can be fixed automatically, run:

```bash
npm run lint:fix
```

### Icons

Icon components live in `src/lib/components/icon/`.

If you need to add a new icon, for consistency search for it in
[Octicons](https://primer.style/octicons/) and only look elsewhere (or make your own!) if no
suitable icons are found.

### Previewing production build

```bash
npm run build
```

You can preview the built app with `npm run preview`. (This should _not_ be used
to serve the app in production, which is done by a [SvelteKit adapter](https://kit.svelte.dev/docs#adapters) (the [Node adapter](https://github.com/sveltejs/kit/tree/master/packages/adapter-node) in our case).)
