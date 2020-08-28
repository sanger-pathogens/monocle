import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";
import "cypress-file-upload";

// Test button exists with data in database (admin user) - DONE
// Test button exists without data in database (admin user) - DONE
// Test no button when logged in as non admin - DONE
// Test drag over with wrong file type shows error - DONE
// Test dropping file shows results, commit and cancel button - DONE
// Test commit disabled when missing institution - DONE
// Test commit changes the database

const MIMETYPE_EXCEL = "application/vnd.ms-excel";
const MIMETYPE_TEXT = "text/plain";
const dragAndDropFile = (fileName, mimeType) => {
  cy.fixture(fileName, "binary")
    .then(Cypress.Blob.binaryStringToBlob)
    .then((fileContent) => {
      cy.get('input[type="file"]').attachFile(
        {
          fileContent,
          fileName,
          mimeType,
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
      dragAndDropFile("test_committable.xlsx", MIMETYPE_EXCEL);

      // changes recongised?
      cy.contains("Added: 3").should("exist");
    });
  });

  it("does not accept file with bad extension file when database is empty", () => {
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
      dragAndDropFile("test.txt", MIMETYPE_TEXT);

      // Filetype not expected
      cy.contains("File type not accepted, sorry!");
    });
  });

  it("Commit button is active when spreadsheet is okay", () => {
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
      dragAndDropFile("test_committable.xlsx", MIMETYPE_EXCEL);

      // commit button should not be diasbled
      cy.contains("Commit").should("not.be.disabled");
    });
  });

  it("Commit button is disabled when spreadsheet has missing institution", () => {
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
      dragAndDropFile("test_missing_institution.xlsx", MIMETYPE_EXCEL);

      // commit button should not be diasbled
      cy.contains("Commit").should("be.disabled");
    });
  });

  it("Table updated when commit button clicked", () => {
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
      dragAndDropFile("test_committable.xlsx", MIMETYPE_EXCEL);

      // commit button should not be diasbled
      cy.contains("Commit").click();
      cy.wait(API_WAIT_MS);
    });
  });

  it.only("Table updated when commit button clicked", () => {
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
      dragAndDropFile("test_committable.xlsx", MIMETYPE_EXCEL);

      cy.contains("Added: 3").should("exist");

      // commit button should not be diasbled
      cy.contains("Cancel").click();
      cy.wait(API_WAIT_MS);
      // Drag and drop should exist

      //
      cy.contains("Added: 3").should.not("exist");
    });
  });
});

// cy.get(`table#sampleTable`).contains("td button", laneId);
