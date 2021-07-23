import { render } from "@testing-library/svelte";
import { session } from "$app/stores";
import Layout from "./__layout.svelte";

jest.mock("$app/stores", () => (
  { session: { set: jest.fn() } }
));

it("populates session w/ a user role from the props", () => {
  const userRole = "user";

  render(Layout, { userRole });

  expect(session.set).toHaveBeenCalledTimes(1);
  expect(session.set).toHaveBeenCalledWith({ user: { role: userRole } });
});
