import "./polyfills";
import "../public/settings";
import React from "react";
import streamSaver from "streamsaver";
import { rest } from "msw";
import { renderHook, act } from "@testing-library/react-hooks";

import { DownloadingProvider, useDownloading } from "./downloading";
import env from "./env";
import { server } from "./test-utils/server";

jest.mock("streamsaver");

describe("streamDownloadsToArchive", () => {
  const laneId = "31663_7#113";
  const encodedLaneId = encodeURIComponent(laneId);
  const wrapper = ({ children }) => (
    <DownloadingProvider>{children}</DownloadingProvider>
  );

  it("calls ctrl.enqueue for each", async () => {
    // mock streamSaver.createWriteStream to avoid writing to file
    let streamContent = "";
    const writableStream = new WritableStream({
      write(chunk) {
        return new Promise((resolve, reject) => {
          streamContent += chunk;
          resolve();
        });
      },
      close() {},
    });
    streamSaver.createWriteStream = jest
      .fn()
      .mockImplementation(() => writableStream);

    // specify api responses
    let called = {
      read1: false,
      read2: false,
      assembly: false,
      annotation: false,
    };
    server.use(
      rest.get(`${env.API_ROOT_URL}read1/${encodedLaneId}`, (req, res, ctx) => {
        called.read1 = true;
        return res(ctx.json({ content: "fake read 1 file" }));
      }),
      rest.get(`${env.API_ROOT_URL}read2/${encodedLaneId}`, (req, res, ctx) => {
        called.read2 = true;
        return res(ctx.json({ content: "fake read 2 file" }));
      }),
      rest.get(
        `${env.API_ROOT_URL}assembly/${encodedLaneId}`,
        (req, res, ctx) => {
          called.assembly = true;
          return res(ctx.json({ content: "fake assembly file" }));
        }
      ),
      rest.get(
        `${env.API_ROOT_URL}annotation/${encodedLaneId}`,
        (req, res, ctx) => {
          called.annotation = true;
          return res(ctx.json({ content: "fake annotation file" }));
        }
      )
    );

    const { result } = renderHook(() => useDownloading(), {
      wrapper,
    });

    expect(result.current.downloadSample).not.toBeNull();

    await act(async () => {
      await result.current.downloadSample(laneId);
    });

    // each API request handler was invoked
    expect(called.read1).toBeTruthy();
    expect(called.read2).toBeTruthy();
    expect(called.assembly).toBeTruthy();
    expect(called.annotation).toBeTruthy();

    // some content was streamed (zipped)
    expect(streamContent.length).toBeGreaterThan(0);
  });
});
