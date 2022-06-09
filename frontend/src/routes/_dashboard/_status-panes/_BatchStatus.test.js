import { render } from "@testing-library/svelte";
import BatchStatus from "./_BatchStatus.svelte";

const BATCHES = {
  received: 24,
  deliveries: [
    {
      name: "Batch 1",
      date: "2020-05-21",
      number: 10,
    },
    {
      name: "Batch 2",
      date: "2020-06-28",
      number: 14,
    },
  ],
};

it("displays the total number of samples received", () => {
  const { container } = render(BatchStatus, { batches: BATCHES });

  expect(container.querySelector("h3").textContent).toBe(
    `${BATCHES.received} Samples Received`
  );
});

it("displays batch data for each batch", () => {
  const roleCell = "cell";

  const { getByRole } = render(BatchStatus, { batches: BATCHES });

  BATCHES.deliveries.forEach(({ name, date, number }) => {
    expect(getByRole(roleCell, { name })).toBeDefined();
    expect(getByRole(roleCell, { name: date })).toBeDefined();
    expect(getByRole(roleCell, { name: number })).toBeDefined();
  });
});
