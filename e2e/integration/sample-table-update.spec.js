import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile, login } from "../utils";
import "cypress-file-upload";

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

  it("update button leads to update page", () => {
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

  it("does not accept file with bad extension file", () => {
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
      cy.contains("File type not accepted.");
    });
  });

  it("Commit button is active when spreadsheet passes tests", () => {
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

  it("Commit modal pops up", () => {
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

      // Modal pops up
      cy.contains(
        "Your commit was successful! Click okay to return to the home page or cancel to upload another spreadsheet."
      ).should("exist");
    });
  });

  it("Clicking clear instead of commit reloads page", () => {
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

      // clear button reloads page and removes stats
      cy.contains("Added: 3").should("exist");
      cy.contains("Clear").click();
      cy.wait(API_WAIT_MS);
      cy.url().should("include", "/update");
      cy.contains("Added: 3").should("not.exist");
      cy.contains("Click or drop a valid metadata file to upload.").should(
        "exist"
      );
    });
  });

  it("Clicking okay on modal takes you back to home page", () => {
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

      // Modal pops up
      cy.contains("Okay").click();
      cy.url().should("include", "/");
    });
  });

  it("Clicking cancel on modal takes you back to update page", () => {
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
      cy.contains("Cancel").click();
      cy.url().should("include", "/update");
      cy.contains("Click or drop a valid metadata file to upload.").should(
        "exist"
      );
    });
  });

  it("Commiting spreadsheet adds samples to the table correctly", () => {
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

      // Modal pops up
      cy.contains("Okay").click();
      cy.url().should("include", "/");

      // Table has 3 samples added
      cy.get("table#sampleTable tbody").find("tr").should("have.length", 3);
      cy.get("table#sampleTable tbody")
        .contains("31663_7#1000")
        .should("exist");
      cy.get("table#sampleTable tbody").contains("31663_7#113").should("exist");
      cy.get("table#sampleTable tbody").contains("31663_7#115").should("exist");
    });
  });

  it("Commiting spreadsheet removes samples correctly", () => {
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

      // load the new file
      dragAndDropFile("test_committable.xlsx", MIMETYPE_EXCEL);

      // commit button should not be diasbled
      cy.contains("Commit").click();
      cy.wait(API_WAIT_MS);

      // Modal pops up
      cy.contains("Okay").click();
      cy.url().should("include", "/");

      // Check samples removed from table
      cy.get("table#sampleTable tbody")
        .contains("32820_2#367")
        .should("not.exist");
      cy.get("table#sampleTable tbody")
        .contains("32820_2#368")
        .should("not.exist");

      // Check samples changed
      cy.get("table#sampleTable tbody")
        .contains("Wellcome Sanger Institute")
        .should("exist");
      cy.get("table#sampleTable tbody")
        .contains("National Reference Laboratories")
        .should("not.exist");
    });
  });
});
