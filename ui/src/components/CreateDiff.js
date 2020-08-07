// import React, { useState } from "react";
// import gql from "graphql-tag";
// import { useMutation, useQuery } from "@apollo/react-hooks";
// import UploadButton from "./UploadButton";

// const DIFF_QUERY = gql`
//   query CompareSamples($samples: [SampleInput!]!) {
//     compareSamples(samples: $samples) {
//       added {
//         laneId
//       }
//       removed {
//         laneId
//       }
//       changed {
//         laneId
//       }
//       same {
//         laneId
//       }
//       missingInstitutions
//     }
//   }
// `;
// const UPDATE_MUTATION = gql`
//   mutation UpdateSamples($samples: [SampleInput!]!) {
//     updateSamples(samples: $samples) {
//       committed
//       diff {
//         added {
//           laneId
//         }
//         removed {
//           laneId
//         }
//         changed {
//           laneId
//         }
//         same {
//           laneId
//         }
//         missingInstitutions
//       }
//     }
//   }
// `;

// const StatefulSpreadsheetLoader = () => {
//   const [sheet, setSheet] = useState(null);
//   const [isCommittable, setIsCommitable] = useState(false);
//   const handler = () => {
//     // ... dragdrop file f, as currently working

//     const jsonContent = xlsx.sheet_to_json(f);
//     setSheet(jsonContent);
//   };
//   const [updateMutation] = useMutation(UPDATE_MUTATION, {
//     variables: { samples: sheet },
//     onCompleted() {
//       useEffect(() => {
//         window.scrollTo(0, 0);
//       }, []);
//     },
//     onError() {
//       alert.show("Something went wrong with the update!");
//     },
//   });
//   return (
//     <React.Fragment>
//       <dragdrop handler={handler} />
//       {sheet ? <Diff sheet={sheet} setIsCommitable={setIsCommitable} /> : null}
//       {isCommittable ? <Button onClick={updateMutation}>Commit</Button> : null}
//     </React.Fragment>
//   );
// };

// const Diff = ({ sheet, setIsCommitable }) => {
//   const { loading, error, data } = useQuery(DIFF_QUERY, {
//     variables: { samples: sheet },
//   });
//   // render nothing
//   if (loading || error || !data) {
//     return null;
//   }
//   // check if can commit
//   const { missingInstitutions } = data;
//   // ...
//   if (checksOk) {
//     setIsCommitable(true);
//   }
//   return true;
// };

// export default StatefulSpreadsheetLoader;
