# Atomic Charge Calculator II Frontend

## Setup

### Prerequisites

- Node version 21+. Using [nvm](https://github.com/nvm-sh/nvm) (or [nvm-windows](https://github.com/coreybutler/nvm-windows)) for node version management is recommended.

ACC II uses [pnpm](https://pnpm.io/) for package management, so it needs to be installed first:

```bash
$ npm install -g pnpm
```

Navigate to the `acc2` directory:
```bash
$ cd acc2
```

### Installing Dependencies

```bash
$ pnpm install
```

### Running in Development Mode

```bash
$ pnpm dev
```

### Run Lint

```bash
$ pnpm lint
```

### Building for Production

```bash
$ pnpm build
```

### Preview Production Build

```bash
$ pnpm preview
```

## Development

You can add new [shadcn](https://ui.shadcn.com/) components using the prepared script:

```bash
$ pnpm ui:add <component-name>
```
