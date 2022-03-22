import { render } from "@testing-library/svelte";
import { Chart } from "frappe-charts";
import SlicedChart from "./SlicedChart.svelte";

jest.mock("frappe-charts");

it("calls the chart library w/ the correct arguments", () => {
  const title = "Chart Title";
  const values = ["😛", "<3"];
  const colors = ["blue", "red"];
  const height = 42;
  const labels = ["XXI", "XXII"];
  const type = "percentage";

  render(SlicedChart, {
    title,
    values,
    height,
    labels,
    type,
    colors
  });

  expect(Chart).toHaveBeenCalledTimes(1);
  const chartRootElement = Chart.mock.calls[0][0];
  expect(chartRootElement.tagName).toBe("DIV");
  const chartOptions = Chart.mock.calls[0][1];
  expect(chartOptions).toMatchObject({
    type,
    height,
    title,
    data: {
      datasets: [{ values }],
      labels,
    }
  });
});
