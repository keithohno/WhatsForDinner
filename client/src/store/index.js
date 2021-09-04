import { createStore } from "vuex";

export default createStore({
  state() {
    return {
      count: 1,
      ingredients: [""]
    };
  },
  mutations: {
    add_ingredient(state, ingredient) {
      state.count++;
      state.ingredients.push(ingredient);
    },
    remove_ingredient(state, index) {
      state.count--;
      state.ingredients.splice(index, 1);
    },
    edit_ingredient(state, payload) {
      state.ingredients[payload.index] = payload.value;
    }
  }
});
