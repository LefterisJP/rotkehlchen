/* istanbul ignore file */
/* eslint-disable max-lines,import/max-dependencies */

import { setupLayouts } from 'virtual:generated-layouts';
import Vue from 'vue';
import Router, { type Route } from 'vue-router';
import { Routes } from '@/router/routes';
import { NoteLocation } from '@/types/notes';

Vue.use(Router);

const base = import.meta.env.VITE_PUBLIC_PATH ? window.location.pathname : '/';

const routes = setupLayouts([
  {
    path: Routes.USER,
    redirect: Routes.USER_LOGIN,
  },
  {
    path: Routes.USER_LOGIN,
    component: async () => await import('../pages/user/login/index.vue'),
    meta: {
      layout: 'auth',
    },
  },
  {
    path: Routes.USER_CREATE,
    component: async () => await import('../pages/user/create/index.vue'),
    meta: {
      layout: 'auth',
    },
  },
  {
    path: Routes.ROOT,
    redirect: Routes.USER_LOGIN,
  },
  {
    path: Routes.DASHBOARD,
    name: 'dashboard',
    component: async () => await import('../pages/dashboard/index.vue'),
    meta: {
      noteLocation: NoteLocation.DASHBOARD,
    },
  },
  {
    path: Routes.ACCOUNTS_BALANCES,
    component: async () => await import('../pages/balances/index.vue'),
    children: [
      {
        path: '',
        name: 'accounts-balances',
        redirect: Routes.ACCOUNTS_BALANCES_BLOCKCHAIN,
      },
      {
        path: Routes.ACCOUNTS_BALANCES_BLOCKCHAIN,
        name: 'accounts-balances-blockchain',
        component: async () => await import('../pages/balances/blockchain/index.vue'),
        meta: {
          noteLocation: NoteLocation.ACCOUNTS_BALANCES_BLOCKCHAIN,
        },
      },
      {
        path: Routes.ACCOUNTS_BALANCES_EXCHANGE,
        name: 'accounts-balances-exchange',
        component: async () => await import('../pages/balances/exchange/index.vue'),
        meta: {
          noteLocation: NoteLocation.ACCOUNTS_BALANCES_EXCHANGE,
        },
      },
      {
        path: `${Routes.ACCOUNTS_BALANCES_EXCHANGE}/:exchange`,
        component: async () => await import('../pages/balances/exchange/index.vue'),
        meta: {
          noteLocation: NoteLocation.ACCOUNTS_BALANCES_EXCHANGE,
        },
        props: true,
      },
      {
        path: Routes.ACCOUNTS_BALANCES_NON_FUNGIBLE,
        name: 'accounts-balances-non-fungible',
        meta: {
          noteLocation: NoteLocation.ACCOUNTS_BALANCES_NON_FUNGIBLE,
        },
        component: async () => await import('../pages/balances/non-fungible/index.vue'),
      },
      {
        path: Routes.ACCOUNTS_BALANCES_MANUAL,
        name: 'accounts-balances-manual',
        meta: {
          noteLocation: NoteLocation.ACCOUNTS_BALANCES_MANUAL,
        },
        component: async () => await import('../pages/balances/manual/index.vue'),
      },
    ],
  },
  {
    path: Routes.NFTS,
    name: 'nfts',
    meta: {
      noteLocation: NoteLocation.NFTS,
    },
    component: async () => await import('../pages/nfts/index.vue'),
  },
  {
    path: Routes.HISTORY,
    component: async () => await import('../pages/history/index.vue'),
    children: [
      {
        path: '',
        name: 'history',
        redirect: Routes.HISTORY_TRADES,
      },
      {
        path: Routes.HISTORY_TRADES,
        name: 'trades',
        meta: {
          noteLocation: NoteLocation.HISTORY_TRADES,
        },
        component: async () => await import('../pages/history/trades/index.vue'),
      },
      {
        path: Routes.HISTORY_DEPOSITS_WITHDRAWALS,
        name: 'deposits-withdrawals',
        meta: {
          noteLocation: NoteLocation.HISTORY_DEPOSITS_WITHDRAWALS,
        },
        component: async () => await import('../pages/history/deposits-withdrawals/index.vue'),
      },
      {
        path: Routes.HISTORY_EVENTS,
        name: 'history-events',
        meta: {
          noteLocation: NoteLocation.HISTORY_EVENTS,
        },
        component: async () => await import('../pages/history/transactions/index.vue'),
      },
    ],
  },
  {
    path: Routes.DEFI,
    component: async () => await import('../pages/defi/index.vue'),
    meta: {
      noteLocation: NoteLocation.DEFI,
    },
    children: [
      {
        path: '',
        name: 'defi',
        redirect: Routes.DEFI_OVERVIEW,
      },
      {
        path: Routes.DEFI_OVERVIEW,
        name: 'defi-overview',
        component: async () => await import('../pages/defi/overview/index.vue'),
      },
      {
        path: Routes.DEFI_DEPOSITS,
        component: async () => await import('../pages/defi/deposits/index.vue'),
        children: [
          {
            path: '',
            name: 'defi-deposits',
            redirect: Routes.DEFI_DEPOSITS_PROTOCOLS,
          },
          {
            path: Routes.DEFI_DEPOSITS_PROTOCOLS,
            name: 'defi-deposits-protocols',
            component: async () => await import('../pages/defi/deposits/protocols/index.vue'),
          },
          {
            path: Routes.DEFI_DEPOSITS_LIQUIDITY,
            component: async () => await import('../pages/defi/deposits/liquidity/index.vue'),
            props: (route: Route) => ({
              location: route.params.location ?? null,
            }),
          },
        ],
      },
      {
        path: Routes.DEFI_LIABILITIES,
        name: 'defi-liabilities',
        component: async () => await import('../pages/defi/liabilities/index.vue'),
      },
      {
        path: Routes.DEFI_AIRDROPS,
        component: async () => await import('../pages/defi/airdrops/index.vue'),
      },
    ],
  },
  {
    path: Routes.STATISTICS,
    name: 'statistics',
    meta: {
      noteLocation: NoteLocation.STATISTICS,
    },
    component: async () => await import('../pages/statistics/index.vue'),
  },
  {
    path: Routes.STAKING,
    meta: {
      noteLocation: NoteLocation.STAKING,
    },
    component: async () => await import('../pages/staking/index.vue'),
    props: (route: Route) => ({ location: route.params.location ?? null }),
  },
  {
    path: Routes.PROFIT_LOSS_REPORTS,
    component: async () => await import('../pages/reports/wrapper.vue'),
    children: [
      {
        path: '',
        component: async () => await import('../pages/reports/index.vue'),
        meta: {
          noteLocation: NoteLocation.PROFIT_LOSS_REPORTS,
        },
      },
      {
        path: Routes.PROFIT_LOSS_REPORT,
        component: async () => await import('../pages/reports/[id].vue'),
        meta: {
          canNavigateBack: true,
          noteLocation: NoteLocation.PROFIT_LOSS_REPORTS,
        },
      },
    ],
  },
  {
    path: Routes.ASSET_MANAGER,
    meta: {
      noteLocation: NoteLocation.ASSETS,
    },
    component: async () => await import('../pages/asset-manager/index.vue'),
    children: [
      {
        path: '',
        name: 'asset-manager',
        redirect: Routes.ASSET_MANAGER_MANAGED,
      },
      {
        path: Routes.ASSET_MANAGER_MANAGED,
        name: 'asset-manager-managed',
        component: async () => await import('../pages/asset-manager/managed/index.vue'),
        props: (route: Route) => ({ identifier: route.query.id ?? null }),
      },
      {
        path: Routes.ASSET_MANAGER_CUSTOM,
        name: 'asset-manager-custom',
        component: async () => await import('../pages/asset-manager/custom/index.vue'),
        props: (route: Route) => ({ identifier: route.query.id ?? null }),
      },
      {
        path: Routes.ASSET_MANAGER_MORE,
        component: async () => await import('../pages/asset-manager/more/index.vue'),
        children: [
          {
            path: '',
            name: 'asset-manager-more',
            redirect: Routes.ASSET_MANAGER_CEX_MAPPING,
          },
          {
            path: Routes.ASSET_MANAGER_NEWLY_DETECTED,
            name: 'asset-manager-newly-detected',
            component: async () => await import('../pages/asset-manager/newly-detected/index.vue'),
          },
          {
            path: Routes.ASSET_MANAGER_CEX_MAPPING,
            name: 'asset-manager-cex-mapping',
            component: async () => await import('../pages/asset-manager/cex-mapping/index.vue'),
          },
        ],
      },
    ],
  },
  {
    path: Routes.PRICE_MANAGER,
    component: async () => await import('../pages/price-manager/index.vue'),
    meta: {
      canNavigateBack: true,
      noteLocation: NoteLocation.PRICE_MANAGER,
    },
    props: true,
    children: [
      {
        path: '',
        name: 'price-manager',
        redirect: Routes.PRICE_MANAGER_LATEST,
      },
      {
        path: Routes.PRICE_MANAGER_LATEST,
        name: 'price-manager-current',
        component: async () => await import('../pages/price-manager/latest/index.vue'),
      },
      {
        path: Routes.PRICE_MANAGER_HISTORIC,
        name: 'price-manager-historic',
        component: async () => await import('../pages/price-manager/historic/index.vue'),
      },
    ],
  },
  {
    path: Routes.ADDRESS_BOOK_MANAGER,
    meta: {
      noteLocation: NoteLocation.ADDRESS_BOOK_MANAGER,
    },
    component: async () => await import('../pages/address-book-manager/index.vue'),
  },
  {
    path: Routes.API_KEYS,
    meta: {
      noteLocation: NoteLocation.API_KEYS,
    },
    component: async () => await import('../pages/settings/api-keys/index.vue'),
    children: [
      {
        path: '',
        redirect: Routes.API_KEYS_ROTKI_PREMIUM,
      },
      {
        path: Routes.API_KEYS_ROTKI_PREMIUM,
        component: async () => await import('../pages/settings/api-keys/premium/index.vue'),
      },
      {
        path: Routes.API_KEYS_EXCHANGES,
        component: async () => await import('../pages/settings/api-keys/exchanges/index.vue'),
      },
      {
        path: Routes.API_KEYS_EXTERNAL_SERVICES,
        component: async () => await import('../pages/settings/api-keys/external/index.vue'),
      },
    ],
  },
  {
    path: Routes.IMPORT,
    name: 'import',
    meta: {
      noteLocation: NoteLocation.IMPORT,
    },
    component: async () => await import('../pages/import/index.vue'),
  },
  {
    path: Routes.SETTINGS,
    component: async () => await import('../pages/settings/index.vue'),
    children: [
      {
        path: '',
        redirect: Routes.SETTINGS_GENERAL,
      },
      {
        path: Routes.SETTINGS_GENERAL,
        meta: {
          noteLocation: NoteLocation.SETTINGS_GENERAL,
        },
        component: async () => await import('../pages/settings/general/index.vue'),
      },
      {
        path: Routes.SETTINGS_ACCOUNTING,
        meta: {
          canNavigateBack: true,
          noteLocation: NoteLocation.SETTINGS_ACCOUNTING,
        },
        component: async () => await import('../pages/settings/accounting/index.vue'),
      },
      {
        path: Routes.SETTINGS_DATA_SECURITY,
        meta: {
          noteLocation: NoteLocation.SETTINGS_DATA_SECURITY,
        },
        component: async () => await import('../pages/settings/data-security/index.vue'),
      },
      {
        path: Routes.SETTINGS_MODULES,
        meta: {
          noteLocation: NoteLocation.SETTINGS_MODULES,
        },
        component: async () => await import('../pages/settings/modules/index.vue'),
      },
    ],
  },
  {
    path: Routes.ASSETS,
    component: async () => await import('../pages/assets/[identifier].vue'),
    meta: {
      canNavigateBack: true,
      noteLocation: NoteLocation.ASSETS,
    },
    props: true,
  },
  {
    path: Routes.LOCATIONS,
    component: async () => await import('../pages/locations/[identifier].vue'),
    meta: {
      canNavigateBack: true,
      noteLocation: NoteLocation.LOCATIONS,
    },
    props: true,
  },
  {
    path: Routes.CALENDAR,
    component: async () => await import('../pages/calendar/index.vue'),
    meta: {
      canNavigateBack: true,
      noteLocation: NoteLocation.CALENDAR,
    },
    props: true,
  },
  ...(checkIfDevelopment()
    ? [
        {
          path: '/playground',
          name: 'playground',
          component: async () => await import('../pages/playground/index.vue'),
        },
      ]
    : []),
]);

export const router = new Router({
  mode: 'hash',
  base,
  scrollBehavior: (to, from, savedPosition) => {
    if (to.hash) {
      const element = document.getElementById(to.hash.replace(/#/, ''));
      if (element) {
        nextTick(() => {
          document.body.scrollTo({ left: 0, top: element.offsetTop });
        });
      }

      return { selector: to.hash };
    }
    else if (savedPosition) {
      document.body.scrollTo(savedPosition.x, savedPosition.y);
      return savedPosition;
    }

    if (from.path !== to.path) {
      document.body.scrollTo(0, 0);
      return { x: 0, y: 0 };
    }
  },
  routes,
});

router.beforeEach((to, from, next) => {
  const store = useSessionAuthStore();
  const logged = store.logged;
  if (logged) {
    if (
      [Routes.USER, Routes.USER_CREATE, Routes.USER_LOGIN].includes(to.path)
    )
      return next(Routes.DASHBOARD);

    next();
  }
  else if (to.path.startsWith(Routes.USER)) {
    next();
  }
  else {
    next(Routes.USER_LOGIN);
  }
});
