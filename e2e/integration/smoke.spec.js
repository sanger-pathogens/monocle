describe("smoke", () => {
  it("loads index.html", () => {
    cy.visit("/");
  });

  it("has page title", () => {
    cy.visit("/");
    cy.title().should("eq", "Monocle | Wellcome Sanger Institute");
  });
});
