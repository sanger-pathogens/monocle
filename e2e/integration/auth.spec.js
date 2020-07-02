import { DB_PROFILES, loadDatabaseProfile, login, logout } from "../utils";

describe("authentication", () => {
  beforeEach(() => {
    // clean auth state
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

      // fill in credentials form and submit
      login(email);

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
      const { email } = user;

      // fill in credentials form and submit
      login(email);

      // click logout button
      logout();

      // credentials form?
      cy.get("input[type=email]").should("exist");
      cy.get("input[type=password]").should("exist");
    });
  });
});
