import { USER_QUERY } from "../user";
import { SAMPLES_LIST_QUERY } from "../components/SamplesTable";
import {
  LOGIN_MUTATION,
  LOGOUT_MUTATION,
  VERIFY_MUTATION,
  REFRESH_MUTATION,
} from "../auth";

export const mockUser = {
  email: "admin@juno.com",
  firstName: "Han",
  lastName: "Solo",
  affiliations: [
    {
      name: "Wellcome Sanger Institute",
      __typename: "Institution",
    },
  ],
  __typename: "User",
};

export const mockSamples = [
  {
    laneId: "31663_7#113",
    sampleId: "5903STDY8059170",
    publicName: "CUHK_GBS177WT_16",
    hostStatus: "SKIN_AND_SOFT_TISSUE_INFECTION",
    serotype: "IA",
    submittingInstitution: {
      name: "National Reference Laboratories",
      country: "Israel",
    },
  },
  {
    laneId: "32820_2#367",
    sampleId: "5903STDY8113194",
    publicName: "JN_IL_ST31578",
    hostStatus: "PNEUMONIA",
    serotype: "VI",
    submittingInstitution: {
      name: "The Chinese University of Hong Kong",
      country: "China",
    },
  },
];

export const mockSamplesList = {
  results: mockSamples,
  totalCount: 2,
};

export const mockLoginSuccess = {
  token:
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImdhcmV0aEBqdW5vLmNvbSIsImV4cCI6MTU5MzYyMjI2MSwib3JpZ0lhdCI6MTU5MzYyMTY2MX0.bBjI3XHMvgLiKZ96nQ16sU0d27nP_rUE5iKPQxfWl6o",
  refreshToken: "bc197db0c2faea54f118270c3412ab8218c6bada",
  payload: {
    email: mockUser.email,
    exp: 1593622261,
    origIat: 1593621661,
  },
  refreshExpiresIn: 1594226461,
};

export const mockLogoutSuccess = {
  deleted: true,
};

export const mockVerifyTokenSuccess = {
  payload: {
    email: "gareth@juno.com",
    exp: 1593794546,
    origIat: 1593793946,
    __typename: "GenericScalar",
  },
  __typename: "Verify",
};

export const mockRefreshTokenSuccess = {
  payload: {
    email: "gareth@juno.com",
    exp: 1593794546,
    origIat: 1593793946,
    __typename: "GenericScalar",
  },
  __typename: "Refresh",
};

export const mockDefaults = {
  user: mockUser,
  samples: mockSamples,
  samplesList: mockSamplesList,
  login: mockLoginSuccess,
  logout: mockLogoutSuccess,
  verify: mockVerifyTokenSuccess,
  refresh: mockRefreshTokenSuccess,
  loginErrors: null,
  logoutErrors: null,
  verifyErrors: null,
  refreshErrors: null,
};
export const generateApiMocks = (mocks = mockDefaults) => {
  const {
    user,
    samplesList,
    login,
    logout,
    verify,
    refresh,
    loginErrors,
    logoutErrors,
    verifyErrors,
    refreshErrors,
  } = mocks;

  // call counts for test assertions
  let called = {
    userQuery: 0,
    samplesListQuery: 0,
    loginMutation: 0,
    logoutMutation: 0,
    verifyMutation: 0,
    refreshMutation: 0,
  };

  // combine data and errors
  const combine = (dataFieldName, dataFieldValue, errors) => {
    let result = {};
    if (dataFieldValue) {
      result.data = {
        [dataFieldName]: dataFieldValue,
      };
    }
    if (errors) {
      result.errors = errors;
    }
    return result;
  };

  return {
    called,
    mocks: [
      {
        request: {
          query: USER_QUERY,
        },
        result: () => {
          called.userQuery += 1;
          return {
            data: {
              me: user,
            },
          };
        },
      },

      {
        request: {
          query: SAMPLES_LIST_QUERY,
          variables: { offset: 0, limit: 10, ordering: "lane_id" },
        },
        result: () => {
          called.samplesListQuery += 1;
          return {
            data: {
              samplesList,
            },
          };
        },
      },
      {
        request: {
          query: LOGIN_MUTATION,
          variables: {
            email: mockUser.email,
            password: mockUser.email.split("@")[0],
          },
        },
        result: () => {
          called.loginMutation += 1;
          return combine("tokenAuth", login, loginErrors);
        },
      },
      {
        request: {
          query: LOGOUT_MUTATION,
        },
        result: () => {
          called.logoutMutation += 1;
          return combine("deleteTokenCookie", logout, logoutErrors);
        },
      },
      {
        request: {
          query: VERIFY_MUTATION,
        },
        result: () => {
          called.verifyMutation += 1;
          return combine("verifyToken", verify, verifyErrors);
        },
      },
      {
        request: {
          query: REFRESH_MUTATION,
        },
        result: () => {
          called.refreshMutation += 1;
          return combine("refreshToken", refresh, refreshErrors);
        },
      },
    ],
  };
};
