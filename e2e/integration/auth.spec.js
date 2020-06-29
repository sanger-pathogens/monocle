import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile } from "../utils";

describe("authentication", () => {
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it("exists", () => {
    cy.visit("/");

    // credentials form?
    cy.get("input[type=email]").should("exist");
    cy.get("input[type=password]").should("exist");
  });

  it("supports login", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      cy.visit("/");

      // credentials
      const user = db.user[0];
      const { email, first_name, last_name } = user;
      const password = email.split("@")[0];

      // fill in credentials
      cy.get("input[type=email]").type(email);
      cy.get("input[type=password]").type(password);
      cy.get("button[type=submit]").click();

      // await logged in page
      cy.wait(API_WAIT_MS);

      // sample table present?
      cy.get(`table#sampleTable`).should("exist");

      // user's name present?
      cy.get("body").should("contain", `${first_name} ${last_name}`);
    });
  });

  it("supports logout", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      cy.visit("/");

      // credentials
      const user = db.user[0];
      const { email, first_name, last_name } = user;
      const password = email.split("@")[0];

      // fill in credentials
      cy.get("input[type=email]").type(email);
      cy.get("input[type=password]").type(password);
      cy.get("button[type=submit]").click();

      // await logged in page
      cy.wait(API_WAIT_MS);

      // logout
      cy.contains("Logout").click();

      // await login page again
      cy.wait(API_WAIT_MS);

      // credentials form?
      cy.get("input[type=email]").should("exist");
      cy.get("input[type=password]").should("exist");
    });
  });
});
