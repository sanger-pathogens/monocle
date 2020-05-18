# UI (React)

This is experimental.

## Stack background
If you've not used React, Material UI and/or GraphQL before, it would be worth running through the following tutorials and documentation.
* [React](https://reactjs.org/tutorial/tutorial.html) - probably easiest to follow the browser-based version first
* [create-react-app](https://create-react-app.dev/)
* [React hooks](https://reactjs.org/docs/hooks-intro.html)
* [Apollo Client](https://www.apollographql.com/docs/react/get-started/)
* [Material UI](https://material-ui.com/)
* [Chrome Dev Tools](https://developers.google.com/web/tools/chrome-devtools) - no need to get too deep with this, but it's handy for debugging

## Development

This UI was bootstrapped with [Create React App](https://github.com/facebook/create-react-app). See their documentation for options.

### Quickstart
Ensure you have `NodeJS` installed (latest should be fine; initial development was on version is v12.9.1). 

Also, install `yarn`, which is a command line package manager for talking to the `npm` registry (there's another command line package manager, also called `npm`).

Load the environment defined by the `package.json` and `yarn.lock` (note: you should not need to update these files manually):
```
yarn install
```

Run the development server, which autoreloads when you edit and save a file:
```
yarn start
```

You should be able to view the UI at `localhost:3000`.
