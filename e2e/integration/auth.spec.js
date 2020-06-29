import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile } from "../utils";

describe("authentication", () => {
  it("exists", () => {
    cy.visit("/");
    cy.get("input[type=email]").should("exist");
    cy.get("input[type=password]").should("exist");
  });

  it("supports login", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // credentials
      const email = db.user[0].email;
      const password = email.split("@")[0];

      // fill in credentials
      cy.get("input[type=email]").type(email);
      cy.get("input[type=password]").type(password);
      cy.get("button[type=submit]").click();

      // await logged in page
      cy.wait(API_WAIT_MS);

      // sample table present?
      cy.get(`table#sampleTable`).should("exist");
    });
  });
});
