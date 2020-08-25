import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";
import "cypress-file-upload";

// Test button exists with data in database (admin user) - DONE
// Test button exists without data in database (admin user) - DONE
// Test no button when logged in as non admin - DONE
// Test drag over activates button (correct file)
// Test drag over with wrong file type shows error
// Test dropping file shows results, commit and cancel button
// Test commit disabled when missing institution
// Test commit changes the database

const MIMETYPE_EXCEL = "application/vnd.ms-excel";
const dragAndDropFile = (fileName) => {
  cy.fixture(fileName, "binary")
    .then(Cypress.Blob.binaryStringToBlob)
    .then((fileContent) => {
      cy.get('input[type="file"]').attachFile(
        {
          fileContent,
          fileName,
          mimeType: MIMETYPE_EXCEL,
        },
        { subjectType: "drag-n-drop" }
      );
    });
  cy.wait(API_WAIT_MS);
};

describe("sample table update", () => {
  it("shows update button above empty samples table as Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // has button?
      cy.contains("Update metadata from spreadsheet").should("exist");
    });
  });

  it("shows update button above non-empty samples table as Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // has button?
      cy.contains("Update metadata from spreadsheet").should("exist");
    });
  });

  it("does not show update button above samples table as non-Sanger user", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[1];
      login(user.email);

      // no button?
      cy.contains("Update metadata from spreadsheet").should("not.exist");
    });
  });

  it("leads to update page", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click the button and await change
      cy.contains("Update metadata from spreadsheet").closest("a").click();
      cy.wait(API_WAIT_MS);

      // new page?
      cy.url().should("include", "/update");
    });
  });

  it("shows a summary of added samples when database is empty", () => {
    loadDatabaseProfile(DB_PROFILES.EMPTY).then((db) => {
      // load and login
      cy.visit("/");
      const user = db.user[0];
      login(user.email);

      // click the button and await change
      cy.contains("Update metadata from spreadsheet").closest("a").click();
      cy.wait(API_WAIT_MS);

      // new page?
      cy.url().should("include", "/update");

      // load the new file
      dragAndDropFile("test.xlsx");

      // changes recongised?
      cy.contains("Added: 3").should("exist");
    });
  });
});
