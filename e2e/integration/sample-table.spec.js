import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile } from "../utils";

describe("sample table", () => {
  it("exists", () => {
    cy.visit("/");
    cy.get("body").should("contain", "Samples");
    cy.get(`table#sampleTable`).should("exist");
  });

  it("is empty when the database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // empty samples table?
      expect(db.sample.length).to.equal(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);

      // table empty?
      cy.get(`table#sampleTable tbody tr`).should("not.exist");
    });
  });

  it("is populated when the database is non-empty", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);

      // table contains database entries?
      db.sample.forEach(({ lane_id }) => {
        cy.get(`table#sampleTable`).contains("td", lane_id);
      });
    });
  });
});
