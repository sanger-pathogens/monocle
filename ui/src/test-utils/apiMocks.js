import { USER_QUERY } from "../user";
import { SAMPLES_QUERY } from "../components/Samples";
import { INSTITUTIONS_QUERY } from "../components/Institutions";
import { LOGIN_MUTATION, LOGOUT_MUTATION } from "../auth";

export const mockUser = {
  email: "admin@juno.com",
  firstName: "Han",
  lastName: "Solo",
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

export const mockInstitutions = [
  {
    name: "Wellcome Sanger Institute",
    country: "United Kingdom",
    latitude: 52.083333,
    longitude: 0.183333,
  },
  {
    name: "National Reference Laboratories",
    country: "Israel",
    latitude: 32.083333,
    longitude: 34.8,
  },
  {
    name: "The Chinese University of Hong Kong",
    country: "China",
    latitude: 22.419722,
    longitude: 114.206792,
  },
];

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

export const mockDefaults = {
  user: mockUser,
  samples: mockSamples,
  institutions: mockInstitutions,
  login: mockLoginSuccess,
  logout: mockLogoutSuccess,
};
export const generateApiMocks = (mocks = mockDefaults) => {
  const { user, samples, institutions, login, logout } = mocks;

  // call counts for test assertions
  let called = {
    userQuery: 0,
    samplesQuery: 0,
    institutionsQuery: 0,
    loginMutation: 0,
    logoutMutation: 0,
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
          query: SAMPLES_QUERY,
        },
        result: () => {
          called.samplesQuery += 1;
          return {
            data: {
              samples,
            },
          };
        },
      },
      {
        request: {
          query: INSTITUTIONS_QUERY,
        },
        result: () => {
          called.institutionsQuery += 1;
          return {
            data: {
              institutions,
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
          return {
            data: {
              tokenAuth: login,
            },
          };
        },
      },
      {
        request: {
          query: LOGOUT_MUTATION,
        },
        result: () => {
          called.logoutMutation += 1;
          return {
            data: {
              deleteTokenCookie: logout,
            },
          };
        },
      },
    ],
  };
};
