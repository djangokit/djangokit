You can add JavaScript or TypeScript modules to this directory to
override the default React client and server entrypoint modules:

## Shared

- context.jsx
- routes.jsx
- wrapper.jsx

## Client

- client.app.jsx
- client.auth.jsx
- client.main.jsx
- client.wrapper.jsx

## Server

- server.app.jsx
- server.auth.jsx
- server.main.jsx
- server.wrapper.jsx

## Wrapping

The most likely thing you'll need to do is wrap your app in some kind of
provider. You can wrap both the client and server apps by adding a
`wrapper.jsx` module like so:

```jsx
export default function Wrapper({ children }) {
  return <SomeProvider>{children}</SomeProvider>;
}
```

You can also wrap the client and server apps separately by adding
`client.wrapper.jsx` and/or `server.wrapper.jsx`.
