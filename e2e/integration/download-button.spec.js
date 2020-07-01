// Check no button when empty database - DONE
// Check existence of button - DONE
// Click on button - DONE
// Check new button opens
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

  it("Button clicked", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);
      //   cy.get(`table#sampleTable`).contains("td button", "31663_7#113").click();
      const stub = cy.stub();
      cy.on("window:alert", stub);
      cy.get(`table#sampleTable`)
        .contains("td button", "31663_7#113")
        .click()
        .then(() => {
          expect(stub.getCall(0)).to.be.calledWith(
            "http://localhost:8001/SampleDownload/31663_7%23113,31663_7#113.tar.gz"
          );
        });
      cy.wait(API_WAIT_MS);
    });
  });

  it("Download file link contains correct attachment", () => {
    cy.request("http://localhost:8001/SampleDownload/31663_7%23113").then(
      (response) => {
        expect(response.headers).to.have.property(
          "content-disposition",
          "attachment; filename=31663_7#113.tar.gz"
        );
        expect(response.status).to.eq(200);
      }
    );
  });
});
