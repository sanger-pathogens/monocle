import { render } from "@testing-library/svelte";
import { Chart } from "frappe-charts";
import StatusChart from "./StatusChart.svelte";

jest.mock("frappe-charts");

beforeEach(() => {
  Chart.mockClear();
});

it("computes correct completion percentage for the title", () => {
  const pending = 66;
  const succeeded = 120;
  const failed = 2;

  render(StatusChart, { values: [pending, succeeded, failed] });

  const chartOptions = Chart.mock.calls[0][1];
  expect(chartOptions.title).toBe("64.9% completed");
});

it("passes the right colors to the chart library", () => {
  render(StatusChart);

  const chartOptions = Chart.mock.calls[0][1];
  expect(chartOptions.colors).toEqual(["light-grey", "light-green", "red"]);
});
