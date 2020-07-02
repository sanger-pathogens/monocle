import { Observable } from "apollo-link";

// see https://github.com/apollographql/apollo-link/issues/646
// usage in apollo-link-error:
// onError(({ graphQLErrors, networkError, operation, forward }) => {
//   ...
//   return promiseToObservable(refreshToken()).flatMap(() => forward(operation));
//   ...
// })
export default (promise) =>
  new Observable((subscriber) => {
    promise.then(
      (value) => {
        if (subscriber.closed) return;
        subscriber.next(value);
        subscriber.complete();
      },
      (err) => subscriber.error(err)
    );
    return subscriber;
  });
