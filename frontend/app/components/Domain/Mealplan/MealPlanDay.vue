<template>
  <RecipeDialogAddToShoppingList
    v-model="shoppingListDialog"
    :recipes="recipes"
    :shopping-lists="shoppingLists"
    @list-created="addShoppingList"
  />
  <GroupMealPlanEntryDialog
    v-model="dialog.open"
    :entry="null"
    :date="dialog.date"
    :end-date="endDate"
    @create="createForTargets"
  />
  <MealPlanDayHeader
    :day="day"
    :end-date="endDate"
    :selectable="!endDate"
    :selected="selectedPlanDays.includes(dayKey)"
    @toggle="toggleSelected"
  />
  <slot />
  <!-- Day Column Actions -->
  <div class="d-flex justify-end">
    <BaseButtonGroup
      v-bind="bindings"
      :buttons="buttons"
    />
  </div>
</template>

<script setup lang="ts">
import { format } from "date-fns";
import { useUserApi } from "~/composables/api";
import { useAddToShoppingListDialog } from "~/composables/shopping-list-page/use-add-to-shopping-list-dialog";
import { selectedPlanDays, usePlanTypeOptions } from "~/composables/use-group-mealplan";
import type { ScaledRecipe } from "~/composables/use-group-mealplan";
import { useHouseholdSelf } from "~/composables/use-households";
import type { PlanEntryCreate, PlanEntryType, PlanEntryOut } from "~/lib/api/types/meal-plan";

interface Props {
  recipes?: ScaledRecipe[];
  day: Date;
  /** Set for a week, whose meals aren't planned for a specific day */
  endDate?: Date | null;
  actions: ReturnType<typeof useMealplans>["actions"];
  /** Every entry on the planner, to tell which meals the selected days are missing */
  meals?: PlanEntryOut[];
}

const { open: shoppingListDialog, shoppingLists, addAllLoading, addAllToList, addShoppingList } = useAddToShoppingListDialog();
const { $globals } = useNuxtApp();
const i18n = useI18n();
const api = useUserApi();
const { household } = useHouseholdSelf();
const planTypeOptions = usePlanTypeOptions();
const props = withDefaults(defineProps<Props>(), {
  recipes: () => [],
  endDate: null,
  meals: () => [],
});

const GENERATED_TYPES: PlanEntryType[] = ["breakfast", "lunch", "dinner"];

const dayKey = computed(() => format(props.day, "yyyy-MM-dd"));
const endDateKey = computed(() => props.endDate ? format(props.endDate, "yyyy-MM-dd") : null);
const scale = computed(() => household.value?.preferences?.defaultMealplanScale || 1);
const busy = ref(false);

function toggleSelected() {
  const days = selectedPlanDays.value;
  selectedPlanDays.value = days.includes(dayKey.value) ? days.filter(d => d !== dayKey.value) : [...days, dayKey.value];
}

/** This day plus the selected days. A week has no day to select, so it acts on its own. */
function targetDays() {
  if (props.endDate) return [dayKey.value];
  return [...new Set([dayKey.value, ...selectedPlanDays.value])].sort();
}

/** Picks one random recipe of `type` and puts it on every day in `days` */
async function randomFor(type: PlanEntryType, days: string[]) {
  const [first, ...rest] = days;
  if (!first) return;

  const { data } = await api.mealplans.setRandom({
    date: first,
    endDate: endDateKey.value,
    entryType: type,
    recipeScale: scale.value,
  });
  if (!data?.recipeId) return;

  await Promise.all(rest.map(date => api.mealplans.createOne({
    date,
    entryType: type,
    recipeId: data.recipeId,
    recipeScale: scale.value,
  })));
}

async function run(task: (days: string[]) => Promise<unknown>) {
  busy.value = true;
  try {
    await task(targetDays());
  }
  finally {
    selectedPlanDays.value = [];
    busy.value = false;
    props.actions.refreshAll();
  }
}

const randomMeal = (type: PlanEntryType) => run(days => randomFor(type, days));

/** Fills each day's missing breakfast, lunch and dinner, with the same recipe on every day missing that meal */
const generateDay = () => run(async (days) => {
  for (const type of GENERATED_TYPES) {
    const missing = days.filter(date => !props.meals.some(meal =>
      meal.date === date && meal.entryType === type && (meal.endDate ?? null) === endDateKey.value,
    ));
    await randomFor(type, missing);
  }
});

function createForTargets(payload: PlanEntryCreate) {
  const days = targetDays();
  // a single day keeps whatever date was picked in the dialog
  if (days.length === 1) return run(() => api.mealplans.createOne(payload));
  return run(days => Promise.all(days.map(date => api.mealplans.createOne({ ...payload, date, endDate: null }))));
}

const dialog = reactive({
  open: false,
  date: null as Date | null,
});

function openDialog() {
  dialog.date = props.day;
  dialog.open = true;
}

const buttons = computed(() => [
  {
    icon: $globals.icons.createAlt,
    text: i18n.t("general.new"),
    event: "create",
  },
  {
    icon: $globals.icons.autoFix,
    text: "Generate day",
    event: "generate",
    loading: busy.value,
  },
  {
    icon: $globals.icons.diceMultiple,
    text: i18n.t("meal-plan.random-meal"),
    event: "random",
    children: planTypeOptions.map(({ text, value }) => ({
      icon: $globals.icons.diceMultiple,
      text,
      event: `random-${value}`,
    })),
  },
  {
    icon: $globals.icons.cartCheck,
    text: props.endDate ? i18n.t("meal-plan.add-week-to-list") : i18n.t("meal-plan.add-day-to-list"),
    event: "shopping-list",
    loading: addAllLoading.value,
    disabled: !props.recipes.length,
  },
]);

const bindings = {
  onCreate: openDialog,
  onGenerate: generateDay,
  onShoppingList: addAllToList,
  ...Object.fromEntries(planTypeOptions.map(({ value }) => [
    `onRandom-${value}`,
    () => randomMeal(value),
  ])),
};
</script>
