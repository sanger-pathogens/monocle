import { API_WAIT_MS, DB_PROFILES, loadDatabaseProfile } from "../utils";

describe("download button", () => {
  it("Button does not exist when the database is empty", () => {
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

  it("Button exists when database contains samples", () => {
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

  // TODO: DownloadButton.onClick handler is using alert only within these tests to check filesaver is
  // handed the correct url and filename. This is why it is stubbed
  it("Button clicked passes correct url and filename", () => {
    loadDatabaseProfile(DB_PROFILES.SMALL).then((db) => {
      // non-empty samples table?
      expect(db.sample.length).to.be.greaterThan(0);

      // load page
      cy.visit("/");
      cy.wait(API_WAIT_MS);
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
