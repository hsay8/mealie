<template>
  <v-container class="mx-0 pa-0">
    <GroupMealPlanEntryDialog
      v-model="dialog.open"
      :entry="dialog.entry"
      :date="null"
      @create="actions.createOne($event)"
      @update="actions.updateOne($event)"
    />
    <MealPlanLayout :mealplans="mealplans">
      <template #default="{ plan, index, day }">
        <MealPlanDay :day="day.date" :end-date="day.endDate" :actions="actions" :recipes="day.recipes" :meals="allMeals">
          <!-- drag a card to another day (on phones, long-press first so a swipe still scrolls); meals are grouped by
               type, so the order within a day isn't kept -->
          <VueDraggable
            v-model="mealsByKey[planKey(plan)]!"
            tag="div"
            :delay="250"
            :delay-on-touch-only="true"
            :touch-start-threshold="5"
            group="meals"
            :data-index="index"
            class="meal-drop-zone py-2"
            :class="{ 'week-meals': plan.endDate }"
            @end="onMove"
          >
            <div
              v-for="(mealplan, i) in mealsByKey[planKey(plan)]"
              :key="mealplan.id"
              class="meal-item mb-2 pl-4 pr-2"
            >
              <p v-if="i === 0 || mealsByKey[planKey(plan)]![i - 1]!.entryType !== mealplan.entryType" class="text-overline my-0">
                {{ getEntryTypeText(mealplan.entryType!) }}
              </p>
              <div class="position-relative">
                <!-- `selected` turns off the card's own link (a bare attribute is "", which it reads as false) -->
                <RecipeCardMobile
                  :selected="true"
                  :recipe-id="mealplan.recipe ? mealplan.recipe.id : ''"
                  :scale="mealplan.recipeScale ?? 1"
                  :slug="mealplan.recipe ? mealplan.recipe.slug : mealplan.title!"
                  :description="mealplan.recipe ? mealplan.recipe.description! : mealplan.text!"
                  :name="mealplan.recipe ? mealplan.recipe.name : mealplan.title!"
                  :image="mealplan.recipe ? mealplan.recipe.image! : undefined"
                  :tags="mealplan.recipe ? mealplan.recipe.tags : []"
                  :height="185"
                  @selected="onCardClick(mealplan)"
                >
                  <template #actions>
                    <!-- ps-4 lines the row up with the title; the type is styled like the servings button, not like a tag -->
                    <div class="meal-actions d-flex align-center ga-1 w-100 ps-4 pb-1" @click.stop>
                      <v-menu>
                        <template #activator="{ props: menuProps }">
                          <v-card v-bind="menuProps" class="pa-1 px-2">
                            <v-icon size="small" class="mr-2">
                              {{ $globals.icons.potSteam }}
                            </v-icon>
                            {{ getEntryTypeText(mealplan.entryType!) }}
                          </v-card>
                        </template>
                        <v-list density="compact">
                          <v-list-item
                            v-for="mealType in planTypeOptions"
                            :key="mealType.value"
                            :title="mealType.text"
                            @click="actions.setType(mealplan, mealType.value)"
                          />
                        </v-list>
                      </v-menu>
                      <v-btn
                        v-if="mealplan.recipe"
                        size="small"
                        variant="text"
                        icon
                        :title="$t('meal-plan.randomize-recipe')"
                        @click="randomizeMeal(mealplan)"
                      >
                        <v-icon>{{ $globals.icons.diceMultiple }}</v-icon>
                      </v-btn>
                      <MealPlanScaleControl v-if="mealplan.recipe" class="ms-auto flex-shrink-0" :meal="mealplan" :actions="actions" />
                    </div>
                  </template>
                </RecipeCardMobile>
                <v-btn
                  class="remove-meal"
                  size="x-small"
                  variant="text"
                  icon
                  :title="$t('meal-plan.remove-from-plan')"
                  @click.stop="actions.deleteOne(mealplan.id)"
                >
                  <v-icon>{{ $globals.icons.close }}</v-icon>
                </v-btn>
              </div>
            </div>
          </VueDraggable>
        </MealPlanDay>
      </template>
    </MealPlanLayout>
  </v-container>
</template>

<script setup lang="ts">
import type { SortableEvent } from "sortablejs";
import { format } from "date-fns";
import { VueDraggable } from "vue-draggable-plus";
import MealPlanScaleControl from "~/components/Domain/Mealplan/MealPlanScaleControl.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import { useUserApi } from "~/composables/api";
import type { MealsByDate } from "~/composables/use-group-mealplan";
import { getEntryTypeText, selectedPlanDays, usePlanTypeOptions } from "~/composables/use-group-mealplan";
import type { PlanEntryOut } from "~/lib/api/types/meal-plan";

const props = defineProps<{
  mealplans: MealsByDate[];
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const api = useUserApi();
const router = useRouter();
const auth = useMealieAuth();
const planTypeOptions = usePlanTypeOptions();
const typeOrder = planTypeOptions.map(({ value }) => value);

const allMeals = computed(() => props.mealplans.flatMap(({ meals }) => meals));

// a week and the day it starts on share a date, so weeks get their own keys
function planKey(plan: MealsByDate) {
  return `${plan.endDate ? "week-" : ""}${plan.date.toString()}`;
}

// Local copy for the drag lists to mutate, each day's meals sorted by type so they read as sections
const mealsByKey = reactive<{ [key: string]: PlanEntryOut[] }>({});
watch(
  () => props.mealplans,
  (plans) => {
    for (const plan of plans) {
      mealsByKey[planKey(plan)] = [...plan.meals].sort(
        (a, b) => typeOrder.indexOf(a.entryType!) - typeOrder.indexOf(b.entryType!),
      );
    }
  },
  { immediate: true, deep: true },
);

function onMove(evt: SortableEvent) {
  const from = parseInt(evt.from.getAttribute("data-index") ?? "");
  const to = parseInt(evt.to.getAttribute("data-index") ?? "");
  if (isNaN(from) || isNaN(to) || from === to) return;

  const dest = props.mealplans[to]!;
  const meal = mealsByKey[planKey(dest)]![evt.newIndex as number]!;
  // moving between a week and a day schedules or unschedules the meal
  props.actions.updateOne({
    ...meal,
    date: format(dest.date, "yyyy-MM-dd"),
    endDate: dest.endDate ? format(dest.endDate, "yyyy-MM-dd") : null,
  });
}

// One click edits the meal and a second click soon after opens the recipe instead, which works for double-taps too
const DOUBLE_CLICK_MS = 300;
let clickTimer: ReturnType<typeof setTimeout> | undefined;
let lastClickedId: string | number | undefined;

function onCardClick(mealplan: PlanEntryOut) {
  if (clickTimer && lastClickedId === mealplan.id) {
    clearTimeout(clickTimer);
    clickTimer = undefined;
    openRecipe(mealplan);
    return;
  }

  clearTimeout(clickTimer);
  lastClickedId = mealplan.id;
  clickTimer = setTimeout(() => {
    clickTimer = undefined;
    editMeal(mealplan);
  }, DOUBLE_CLICK_MS);
}

function openRecipe(mealplan: PlanEntryOut) {
  if (!mealplan.recipe) return editMeal(mealplan);

  const scale = mealplan.recipeScale ?? 1;
  const path = `/g/${auth.user.value?.groupSlug}/r/${mealplan.recipe.slug}`;
  router.push(scale === 1 ? path : `${path}?scale=${scale}`);
}

const dialog = reactive({
  open: false,
  entry: null as PlanEntryOut | null,
});

function editMeal(mealplan: PlanEntryOut) {
  if (!mealplan.entryType) return;

  dialog.entry = mealplan;
  dialog.open = true;
}

async function randomizeMeal(mealplan: PlanEntryOut) {
  if (!mealplan.entryType) return;

  // Create the new random entry first, so a failure here doesn't lose the current entry
  const { data: created } = await api.mealplans.setRandom({
    date: mealplan.date,
    endDate: mealplan.endDate,
    entryType: mealplan.entryType,
    recipeScale: mealplan.recipeScale,
  });

  if (created) {
    await api.mealplans.deleteOne(mealplan.id);
    props.actions.refreshAll();
  }
}

onUnmounted(() => {
  selectedPlanDays.value = [];
});
</script>

<style scoped>
/* an empty day still needs room to drop a meal on */
.meal-drop-zone {
  min-height: 64px;
}

/* a long press drags the card, so keep phones from selecting text or opening the image menu instead */
.meal-item {
  user-select: none;
  -webkit-touch-callout: none;
}

/* the type and Serves buttons: outlined in the text colour (black in light, white in dark), no fill */
.meal-actions :deep(.v-card) {
  background: transparent !important;
  color: rgb(var(--v-theme-on-surface)) !important;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.6) !important;
  box-shadow: none !important;
  backdrop-filter: none;
}

.remove-meal {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 1;
}
</style>
