import React, { useMemo } from "react";
import { useLazyQuery } from "@apollo/react-hooks";
import gql from "graphql-tag";
import { LinearProgress } from "@material-ui/core";

import DataTable, { camelCaseToSnakeCase } from "./DataTable";
import { useDownloading } from "../downloading";
import SampleDownloadButton from "./SampleDownloadButton";

export const SAMPLES_LIST_QUERY = gql`
  query SamplesList($offset: Int, $limit: Int, $ordering: String) {
    samplesList {
      results(limit: $limit, offset: $offset, ordering: $ordering) {
        laneId
        sampleId
        publicName
        hostStatus
        serotype
        submittingInstitution {
          name
          country # TODO: replace submittingInstitution.country with samples.country
        }
      }
      totalCount
    }
  }
`;

const Samples = () => {
  const { isDownloading } = useDownloading();
  const columns = useMemo(
    () => [
      {
        Header: "Metadata",
        columns: [
          {
            Header: "Lane ID",
            accessor: "laneId",
          },
          {
            Header: "Sample ID",
            accessor: "sampleId",
          },
          {
            Header: "Public Name",
            accessor: "publicName",
          },
          {
            Header: "Submitter",
            accessor: "submittingInstitution.name",
          },
          {
            Header: "Host Status",
            accessor: "hostStatus",
          },
          {
            Header: "Serotype",
            accessor: "serotype",
          },
          {
            Header: "Actions",
            canSort: false,
            Cell: ({ row }) => (
              <SampleDownloadButton laneId={row.original.laneId} />
            ),
          },
        ],
      },
    ],
    []
  );
  const sortBy = useMemo(() => [{ id: "laneId", desc: false }], []);

  // see https://github.com/tannerlinsley/react-table/discussions/2296
  let [loadData, { loading, error, data }] = useLazyQuery(SAMPLES_LIST_QUERY);

  const fetchIdRef = React.useRef(0);

  const fetchData = React.useCallback(
    ({ pageSize, pageIndex, sortBy }) => {
      const fetchId = ++fetchIdRef.current;
      if (fetchId === fetchIdRef.current) {
        // map react-table state to api arguments
        const offset = pageSize * pageIndex;
        const limit = pageSize;
        const ordering =
          sortBy && sortBy.length === 1
            ? `${sortBy[0].desc ? "-" : ""}${camelCaseToSnakeCase(
                sortBy[0].id
              )}`
            : "lane_id";

        // call api
        loadData({
          variables: {
            offset,
            limit,
            ordering,
          },
        });
      }
    },
    [loadData]
  );

  const pageSize = 10;
  const pageCount = data
    ? Math.ceil(data.samplesList.totalCount / pageSize)
    : 0;
  const allData = data ? data.samplesList.results : [];
  const totalCount = data ? data.samplesList.totalCount : 0;

  return (
    <React.Fragment>
      {isDownloading || loading ? <LinearProgress color="secondary" /> : null}
      <DataTable
        tableId="sampleTable"
        columns={columns}
        data={allData}
        totalCount={totalCount}
        fetchData={fetchData}
        loading={loading}
        error={error}
        pageCount={pageCount}
        pageSize={pageSize}
        sortBy={sortBy}
      />
    </React.Fragment>
  );
};

export default Samples;
