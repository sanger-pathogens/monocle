import React from "react";
import { render, fireEvent, act } from "@testing-library/react";

import { DownloadingContext } from "../downloading";
import SampleDownloadButton from "./SampleDownloadButton";

describe("SampleDownloadButton", () => {
  const laneId = "31663_7#113";

  it("should call the downloadSample on click", async () => {
    const isDownloading = false;
    const downloadSample = jest.fn();

    const { getByLabelText } = render(
      <DownloadingContext.Provider value={{ isDownloading, downloadSample }}>
        <SampleDownloadButton laneId={laneId} />
      </DownloadingContext.Provider>
    );

    act(() => {
      fireEvent.click(getByLabelText(laneId));
    });

    expect(getByLabelText(laneId)).toBeInTheDocument();
    expect(downloadSample).toHaveBeenCalled();
  });

  it("should be disabled if in a downloading state", async () => {
    const isDownloading = true;
    const downloadSample = jest.fn();

    const { getByLabelText } = render(
      <DownloadingContext.Provider value={{ isDownloading, downloadSample }}>
        <SampleDownloadButton laneId={laneId} />
      </DownloadingContext.Provider>
    );

    expect(getByLabelText(laneId)).toBeInTheDocument();
    expect(getByLabelText(laneId).closest("button")).toBeDisabled();
  });
});
