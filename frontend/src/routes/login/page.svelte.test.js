import { fireEvent, render, waitFor } from "@testing-library/svelte";
import { HTTP_POST, HTTP_HEADERS_JSON } from "$lib/constants.js";
import LoginPage from "./+page.svelte";

const LABEL_LOG_IN = "Log in";
const LABEL_PASSWORD = "Password";
const LABEL_USERNAME = "Username";
const LOGIN_ENDPOINT = "/auth";
const ROLE_BUTTON = "button";
const USERNAME = "some username";
const PASSWORD = "some password";

global.fetch = jest.fn(() => Promise.resolve());

it("submits a username and password to the correct endpoint on clicking the submit button", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);
  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }));

  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith(LOGIN_ENDPOINT, {
    method: HTTP_POST,
    headers: HTTP_HEADERS_JSON,
    body: JSON.stringify({ username: USERNAME, password: PASSWORD }),
  });
});

it("submits a username and password to the correct endpoint on submitting the form directly", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);
  fetch.mockClear();
  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  fireEvent.submit(getByRole("form"));

  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith(LOGIN_ENDPOINT, {
    method: HTTP_POST,
    headers: HTTP_HEADERS_JSON,
    body: JSON.stringify({ username: USERNAME, password: PASSWORD }),
  });
});

it("disables the submit button if a username or password is empty", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeTruthy();

  await fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeTruthy();

  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: "  " },
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeTruthy();

  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeFalsy();
});

it("disables the submit button while the form is being submitted", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeTruthy();

  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeFalsy();

  fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }));

  await waitFor(() => {
    expect(
      getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled
    ).toBeTruthy();
  });
  await waitFor(() => {
    expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeFalsy();
  });
});

it("redirects to the URL from a response on submit", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);
  const baseUrl = "https://www.example.com";
  const expectedRedirectUrl = `${baseUrl}/some-path`;
  fetch.mockResolvedValueOnce({ redirected: true, url: expectedRedirectUrl });
  delete global.location;
  global.location = new URL(baseUrl);
  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }));

  await waitFor(() => {
    expect(global.location.href).toBe(expectedRedirectUrl);
  });
});

it("clears the session storage before redirecting on successful login", async () => {
  Storage.prototype.clear = jest.fn();
  const { getByRole, getByLabelText } = render(LoginPage);
  fetch.mockResolvedValueOnce({ redirected: true });
  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  expect(sessionStorage.clear).not.toHaveBeenCalled();

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }));

  expect(sessionStorage.clear).toHaveBeenCalledTimes(1);
});

it("shows an error message on login error and re-enables the submit button", async () => {
  const { getByRole, getByLabelText } = render(LoginPage);
  global.alert = jest.fn();
  fetch.mockRejectedValueOnce();
  fireEvent.input(getByLabelText(LABEL_USERNAME), {
    target: { value: USERNAME },
  });
  await fireEvent.input(getByLabelText(LABEL_PASSWORD), {
    target: { value: PASSWORD },
  });

  await fireEvent.click(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }));

  expect(alert).toHaveBeenCalledTimes(1);
  expect(alert).toHaveBeenCalledWith(
    "An error occured while submitting the credentials. Please try again and contact us if the problem persists."
  );
  await waitFor(() => {
    expect(getByRole(ROLE_BUTTON, { name: LABEL_LOG_IN }).disabled).toBeFalsy();
  });
});
