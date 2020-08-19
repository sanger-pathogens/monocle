import React from "react";
import { useLazyQuery } from "@apollo/react-hooks";
import gql from "graphql-tag";

import DataTable from "./DataTable";
import { useDownloading } from "../downloading";
import SampleDownloadButton from "./SampleDownloadButton";

export const SAMPLES_LIST_QUERY = gql`
  query SamplesList($offset: Int, $limit: Int) {
    samplesList {
      results(limit: $limit, offset: $offset) {
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
  const columns = React.useMemo(
    () => [
      {
        Header: "Metadata",
        columns: [
          {
            Header: "Lane ID",
            accessor: "laneId",
            // canSort: true
          },
        ],
      },
    ],
    []
  );

  //   https://github.com/tannerlinsley/react-table/discussions/2296
  let [loadData, { loading, error, data }] = useLazyQuery(SAMPLES_LIST_QUERY);

  const fetchIdRef = React.useRef(0);

  const fetchData = React.useCallback(({ pageSize, pageIndex }) => {
    // sortBy
    const fetchId = ++fetchIdRef.current;
    if (fetchId === fetchIdRef.current) {
      const offset = pageSize * pageIndex;
      const limit = pageSize;
      loadData({
        variables: {
          offset,
          limit,
        },
      });
    }
  }, []);

  const pageSize = 10;
  const pageCount = data
    ? Math.ceil(data.samplesList.totalCount / pageSize)
    : 0;
  const allData = data ? data.samplesList.results : [];

  return (
    <DataTable
      columns={columns}
      data={allData}
      fetchData={fetchData}
      loading={loading}
      pageCount={pageCount}
      pageSize={pageSize}
    />
  );
};

export default Samples;
