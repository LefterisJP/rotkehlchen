import { type Wrapper, mount } from '@vue/test-utils';
import UserSecuritySettings from '@/pages/settings/data-security/index.vue';
import { libraryDefaults } from '../../../utils/provide-defaults';

vi.mock('@/services/backup', () => ({
  useBackupApi: () => ({
    info: vi.fn(),
  }),
}));

describe('userSecuritySettings.vue', () => {
  let wrapper: Wrapper<any>;

  function createWrapper() {
    const pinia = createPinia();
    setActivePinia(pinia);
    return mount(UserSecuritySettings, {
      pinia,
      stubs: [
        'card-title',
        'asset-select',
        'asset-update',
        'confirm-dialog',
        'data-table',
      ],
      provide: libraryDefaults,
    });
  }

  beforeEach(() => {
    wrapper = createWrapper();
  });

  it('displays no warning by default', () => {
    expect(wrapper.find('[data-cy=premium-warning]').exists()).toBe(false);
  });

  it('displays warning if premium sync enabled', async () => {
    const { premiumSync } = storeToRefs(usePremiumStore());
    set(premiumSync, true);
    await nextTick();
    expect(wrapper.find('[data-cy=premium-warning]').exists()).toBe(true);
  });
});
