// Check no button when empty database - DONE
// Check existence of button - DONE
// Click on button
// Check file has downloaded
// Check downloaded file contains correct data
import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile } from "../utils";

describe("download button", () => {
  it("button does not exist when the database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // empty samples table?
      expect(db.sample.length).to.equal(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);

      // button does not exist
      //   cy.get("td button").should("not.exist");
      cy.get(`table#sampleTable`)
        .contains("td button", "31663_7#113")
        .should("not.exist");
    });
  });

  it("button exists when database contains samples", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);

      // button exists
      cy.get(`table#sampleTable`).contains("td button", "31663_7#113");
    });
  });

  it("File downloaded when button clicked", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);

      cy.get(`table#sampleTable`).contains("td button", "31663_7#113").click();
    });
  });
});
